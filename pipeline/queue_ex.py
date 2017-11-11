from queue import Empty
from multiprocessing import Queue
from multiprocessing import JoinableQueue

if __name__=='__main__':
    q = Queue()
    q.put('Hello')
    result = q.get()
    try:
        data = q.get_nowait()
    except Empty:
        data = None
    try:
        more = q.get(timeout=2.5)
    except Empty:
        more = None
