import threading
from src.util import DotDict


# global variables
# use lock for prevent simultaneously running
job_lock = threading.Lock()
# use queue for prevent re-queue
queue = DotDict(
    {
        "ping_connect": False,
        "ping_disconnect": False,
        "speed_test": False
    }
)
