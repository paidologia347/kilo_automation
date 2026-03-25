from collections import deque
from threading import Lock


class Empty(Exception):
    pass


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
    for prompt in prompts:
        task_queue.put(prompt)
