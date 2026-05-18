import time
import asyncio
import tqdm
import concurrent.futures

from src.util import DotDict, create_packs
from src.config import Config
from src.cron import job_lock, queue

SOFT_DELETE_DISCONNECTED = False
PER_PROXY_BUDGET = 5.0  # total seconds allowed per proxy before timing out
SOFT_DELETE_WORKERS = 8
TCP_PROBE_TIMEOUT = 1.5  # seconds for TCP connect probe
TCP_PROBE_CONCURRENCY = 500  # max concurrent TCP probes


async def _tcp_probe_one(server, port, sem):
    async with sem:
        try:
            fut = asyncio.open_connection(server, port)
            _, writer = await asyncio.wait_for(fut, timeout=TCP_PROBE_TIMEOUT)
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
            return True
        except Exception:
            return False


async def _tcp_probe_batch(proxies):
    sem = asyncio.Semaphore(TCP_PROBE_CONCURRENCY)
    return await asyncio.gather(
        *(_tcp_probe_one(p["server"], p["port"], sem) for p in proxies)
    )


def _tcp_filter(proxies):
    """Quickly drop proxies whose TCP port isn't reachable. Returns (alive, dead)."""
    if not proxies:
        return [], []
    loop = asyncio.new_event_loop()
    try:
        results = loop.run_until_complete(_tcp_probe_batch(proxies))
    finally:
        loop.close()
    alive, dead = [], []
    for p, ok in zip(proxies, results):
        (alive if ok else dead).append(p)
    return alive, dead


def _task_function(telegram_api, proxy):
    deadline = time.time() + PER_PROXY_BUDGET
    samples = []
    while True:
        remaining = deadline - time.time()
        if remaining <= 0:
            break
        result = telegram_api.ping_proxy(proxy.td_proxy_id, timeout=remaining)
        if not result.error:
            samples.append(result.update["seconds"] * 1000)
            break
    return samples, proxy.id


def _batch_soft_delete(server, proxy_ids):
    if not proxy_ids:
        return
    print(f"soft_delete batch ({len(proxy_ids)} proxies)")
    with concurrent.futures.ThreadPoolExecutor(max_workers=SOFT_DELETE_WORKERS) as ex:
        list(ex.map(server.soft_delete_proxy, proxy_ids))


def _start(server, telegram_api, proxies):
    batch = Config.batch_size_ping
    pack_proxies = create_packs(proxies, batch)
    for pack in tqdm.tqdm(pack_proxies):
        print("job-ping start packet")
        start_time = time.time()
        telegram_api.remove_all_proxies()
        # add proxies to TDLib (enable=False: don't switch active connection)
        for i in range(0, len(pack)):
            proxy = DotDict(pack[i])
            proxy.error = False
            result = telegram_api.add_proxy(
                proxy.server, proxy.port, proxy.secret, enable=False
            )
            if result.error:
                proxy.error = True
                pack[i] = proxy
                err = result.error_info["message"]
                if err == "Wrong proxy secret" or err == "Unsupported proxy secret":
                    print("send delete proxy request.")
                    server.delete_proxy(proxy.id)
                continue
            proxy.td_proxy_id = result.update["id"]
            pack[i] = proxy

        # ping in parallel
        reports = []
        disconnected_ids = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for proxy in pack:
                if proxy.error:
                    continue
                futures.append(executor.submit(_task_function, telegram_api, proxy))
            for future in concurrent.futures.as_completed(futures):
                samples, proxy_id = future.result()
                if not samples:
                    if SOFT_DELETE_DISCONNECTED:
                        disconnected_ids.append(proxy_id)
                    else:
                        reports.append({"proxy_id": proxy_id, "ping": -1})
                else:
                    ping_ms = min(samples)
                    print(ping_ms)
                    reports.append({"proxy_id": proxy_id, "ping": ping_ms})

        print(reports)
        server.send_ping_report({"reports": reports})
        _batch_soft_delete(server, disconnected_ids)
        elapsed_time = time.time() - start_time
        print(f"job-ping packet sent elapsed_time: {elapsed_time}")
    telegram_api.remove_all_proxies()


def _start_ping(server, telegram_api, disconnect):
    result = server.get_ping_proxies(disconnect)
    if not result:
        print("no result fetched.")
        return
    proxies = result["result"]
    if not proxies:
        return

    # Stage 1: cheap TCP probe to drop obviously-dead proxies
    t0 = time.time()
    print(f"TCP probe: {len(proxies)} proxies (concurrency={TCP_PROBE_CONCURRENCY})")
    candidates, dead = _tcp_filter(proxies)
    print(
        f"TCP probe: {len(candidates)}/{len(proxies)} reachable in {time.time()-t0:.1f}s"
    )
    # Report TCP-unreachable as ping=-1 so the server can track disconnect state
    if dead:
        reports = [{"proxy_id": p["id"], "ping": -1} for p in dead]
        server.send_ping_report({"reports": reports})

    # Stage 2: real MTProto pingProxy via TDLib (only on TCP-alive candidates)
    if candidates:
        _start(server, telegram_api, candidates)


def start_safe(server, telegram_api, disconnect):
    global job_lock, queue
    if disconnect:
        if queue.ping_disconnect:
            return
        queue.ping_disconnect = True
        with job_lock:
            _start_ping(server, telegram_api, disconnect)
        queue.ping_disconnect = False
        return
    else:
        if queue.ping_connect:
            return
        queue.ping_connect = True
        with job_lock:
            _start_ping(server, telegram_api, disconnect)
        queue.ping_connect = False
        return
