from collections import deque
import logging
from threading import Lock


class Empty(Exception):
    pass


logger = logging.getLogger(__name__)


class TaskQueue:
    def __init__(self):
        self._items = deque()
        self._lock = Lock()

    def put(self, item, block=True, timeout=None):
        with self._lock:
            self._items.append(item)

    def get(self, block=True, timeout=None):
        with self._lock:
            if not self._items:
                raise Empty("Queue is empty")
            return self._items.popleft()

    def empty(self):
        with self._lock:
            return not self._items

    def task_done(self):
        return None


class Queue(TaskQueue):
    pass


task_queue = TaskQueue()


def add_tasks(prompts):
    try:
        for prompt in prompts:
            task_queue.put(prompt)
    except Exception as error:
        logger.exception("Failed to add prompts to queue: %s", error)
        raise
