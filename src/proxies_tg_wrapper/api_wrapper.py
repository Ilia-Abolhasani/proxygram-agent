import telegram.client as client


class DotDict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Telegram_API:
    def __init__(
        self,
        api_id,
        api_hash,
        phone,
        database_encryption_key,
        tdlib_directory,
        library_path=None,
        proxy_server=None,
        proxy_port=None,
        proxy_secret=None,
        skip_login=False,
    ):
        if proxy_server:
            self.tg = client.Telegram(
                api_id=api_id,
                api_hash=api_hash,
                phone=phone,
                database_encryption_key=database_encryption_key,
                files_directory=tdlib_directory,
                library_path=library_path,
                proxy_server=proxy_server,
                proxy_port=proxy_port,
                proxy_type={"@type": "proxyTypeMtproto", "secret": proxy_secret},
            )
        else:
            self.tg = client.Telegram(
                api_id=api_id,
                api_hash=api_hash,
                phone=phone,
                database_encryption_key=database_encryption_key,
                files_directory=tdlib_directory,
                library_path=library_path,
            )
        if skip_login:
            self._init_tdlib_only()
        else:
            self.tg.login(blocking=True)

    def _init_tdlib_only(self):
        """Initialize TDLib (set params + encryption key) without full login."""
        from telegram.client import AuthorizationState

        stop_states = (
            AuthorizationState.WAIT_PHONE_NUMBER,
            AuthorizationState.WAIT_CODE,
            AuthorizationState.WAIT_PASSWORD,
            AuthorizationState.WAIT_REGISTRATION,
            AuthorizationState.READY,
        )

        actions = {
            AuthorizationState.NONE: self.tg.get_authorization_state,
            AuthorizationState.WAIT_TDLIB_PARAMETERS: self.tg._set_initial_params,
            AuthorizationState.WAIT_ENCRYPTION_KEY: self.tg._send_encryption_key,
        }

        while self.tg.authorization_state not in stop_states:
            action = actions.get(self.tg.authorization_state)
            if action is None:
                break
            result = action()
            self.tg.authorization_state = self.tg._wait_authorization_result(result)

    def __del__(self):
        self.tg.stop()

    def _call(self, method_name, params, timeout=None):
        result = self.tg.call_method(method_name=method_name, params=params)
        try:
            result.wait(timeout=timeout)
        except TimeoutError:
            result.error = True
            result.error_info = {"message": "Timeout"}
        return result

    def _dot(self, dict):
        return DotDict(dict)

    def set_log_verbose_level(self, new_verbosity_level):
        # level 0: fatal errors
        # level 1: erroes
        # level 2: warning & debug
        # level 3: info
        # level 4: debug
        # level 5: verbose debu
        result = self._call(
            "setLogVerbosityLevel", {"new_verbosity_level": new_verbosity_level}
        )
        return result

    def send_message(
        self,
        message_text,
        chat_id,
        message_thread_id=0,
        reply_to_message_id=0,
        options=None,
        reply_markup=None,
    ):
        input_message_content = {
            "@type": "inputMessageText",
            "text": {"@type": "formattedText", "text": message_text, "entities": []},
            "disable_web_page_preview": False,
            "clear_draft": False,
        }
        result = self._call(
            "sendMessage",
            {
                "chat_id": chat_id,
                "message_thread_id": message_thread_id,
                "reply_to_message_id": reply_to_message_id,
                "options": options,
                "reply_markup": reply_markup,
                "input_message_content": input_message_content,
            },
        )
        return result

    def download_file(self, file_id, priority):
        result = self._call(
            "downloadFile",
            {"file_id": file_id, "priority": priority, "synchronous": True},
        )
        return result

    def cancel_download_file(self, file_id, only_if_pending):
        result = self._call(
            "cancelDownloadFile",
            {
                "file_id": file_id,
                "only_if_pending": only_if_pending,
            },
        )
        return result

    def add_proxy(self, server, port, secret):
        return self._call(
            "addProxy",
            {
                "server": server,
                "port": port,
                "enable": True,
                "type": {"@type": "proxyTypeMtproto", "secret": secret},
            },
        )

    def enable_proxy(self, proxy_id):
        return self._call("enableProxy", {"proxy_id": proxy_id})

    def remove_proxy(self, proxy_id):
        return self._call("removeProxy", {"proxy_id": proxy_id})

    def ping_proxy(self, proxy_id, timeout=None):
        return self._call("pingProxy", {"proxy_id": proxy_id}, timeout=timeout)

    def get_proxies(self):
        result = self._call("getProxies", {})
        if not result.update:
            return []
        proxies = result.update["proxies"]
        output = []
        for proxy in proxies:
            output.append(self._dot(proxy))
        return output

    def remove_all_proxies(self):
        proxies = self.get_proxies()
        for proxy in proxies:
            self.remove_proxy(proxy.id)

    def search_public_chat(self, username):
        result = self._call("searchPublicChat", {"username": username})
        return result.update["id"]

    def get_message(self, chat_id, message_id):
        return self._call("getMessage", {"chat_id": chat_id, "message_id": message_id})

    def get_chat_history(self, chat_id, limit, from_message_id, offset, only_local):
        result = self._call(
            "getChatHistory",
            {
                "chat_id": chat_id,
                "limit": limit,
                "from_message_id": from_message_id,
                "offset": offset,
                "only_local": only_local,
            },
        )
        return result

    def channel_history(self, chat_id, limit, min_message_id):
        last_message_id = None
        from_message_id = 0
        counter = 0
        recived_messages = []
        flag = True
        while flag:
            result = self.get_chat_history(chat_id, 50, from_message_id, 0, False)
            if result.error:
                raise Exception(
                    f"Error happend in fetch channel_history, chat_id {chat_id} "
                    + str(result.error_info["message"])
                )
            if result.update["total_count"] == 0:
                break
            for message in result.update["messages"]:
                counter += 1
                message_id = message["id"]
                from_message_id = message_id
                if min_message_id and message_id <= min_message_id:
                    flag = False
                    break
                if not last_message_id:
                    last_message_id = message_id
                recived_messages.append(message)
                if counter >= limit:
                    flag = False
                    break
        if not last_message_id and min_message_id:
            last_message_id = min_message_id
        return recived_messages, last_message_id

    def view_messages(self, chat_id, message_ids):
        """
        Mark messages as read in a chat.

        Args:
            chat_id: The chat ID where the messages are
            message_ids: List of message IDs to mark as read
        """
        try:
            result = self._call(
                "viewMessages",
                {
                    "chat_id": chat_id,
                    "message_ids": message_ids,
                    "force_read": True,  # Mark as read even if current user is not a member
                },
            )
            return result
        except Exception as e:
            print(f"Error marking messages as read: {e}")
            return None

    def idle(self):
        self.tg.idle()

    def stop(self):
        # tg stoped
        self.tg.stop()
