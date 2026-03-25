from queue import Queue
task_queue = Queue()

def add_tasks(prompts):
    for p in prompts:
        task_queue.put(p)
