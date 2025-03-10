import queue
import threading
import time

from typing import Callable, Optional, Sequence

def parallelize_over(seq: Sequence,
                     batch_size: Optional[int] = None,
                     num_batches: Optional[int] = None):

    if batch_size is not None and num_batches is not None:
        raise ValueError("cannot specify both batch_size and num_batches")

    if batch_size is None:
        if num_batches is None:
            batch_size = 1
        else:
            batch_size = len(seq) // num_batches

    def parallelize_over_decorator(func: Callable):
        threads = []

        work_queue = queue.Queue()
        def worker():
            while True:
                segment = work_queue.get()
                if segment is None:
                    # terminate thread
                    work_queue.task_done()
                    break

                for i in segment:
                    func(i)
                work_queue.task_done()

        for _ in range(12):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        print("started threads")

        n = len(seq)
        for start in range(0, n, batch_size):
            end = min(n, start + batch_size)
            work_queue.put(seq[start:end])
        for _ in threads:
            # thread terminators
            work_queue.put(None)
        print("added items to queue")

        work_queue.join()
        for thread in threads:
            thread.join()
        print("DONE EXECUTING")

    return parallelize_over_decorator

for i in range(10):
    _ = 10 ** 3 + i


@parallelize_over(range(int(1e2)))
def loop_body(i: int):
    _ = 10 ** 3 + i

