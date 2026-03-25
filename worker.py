from queue import task_queue
from utils.browser import generate
from utils.upscale import upscale
from utils.metadata import meta
from utils.uploader import upload

def run_workers():
    while not task_queue.empty():
        p = task_queue.get()
        f = generate(p)
        f = upscale(f)
        meta(f,p)
        upload(f)
        task_queue.task_done()
