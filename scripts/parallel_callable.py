import queue
import threading
import time

from typing import Any, Callable, Optional, Protocol, Sequence, TypeVar, overload

T = TypeVar('T', contravariant=True)

class ParallelFunction(Protocol[T]):
    # @overload
    # def __call__(self, __item: T) -> Any: ...
    # @overload
    # def __call__(self, __item: T, *args: Any) -> Any: ...
    # @overload
    # def __call__(self, __item: T, **kwargs: Any) -> Any: ...
    # @overload
    def __call__(self, __item: T, *args: Any, **kwargs: Any) -> Any: ...

def parallelize_over(seq: Sequence[T],
                     fn: ParallelFunction[T],
                     *args,
                     **kwargs):

    batch_size = None
    num_batches = None
    if batch_size is not None and num_batches is not None:
        raise ValueError("cannot specify both batch_size and num_batches")

    if batch_size is None:
        if num_batches is None:
            batch_size = 1
        else:
            batch_size = len(seq) // num_batches

    threads = []

    work_queue: queue.Queue = queue.Queue()
    def worker():
        while True:
            segment = work_queue.get()
            if segment is None:
                # terminate thread
                work_queue.task_done()
                break

            for i in segment:
                fn(i, *args, **kwargs)
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


def body1(i: int):
    print(i)

parallelize_over(range(10), body1)


def body2(s: str):
    print(s)

arr = ['hi', 'bye']
parallelize_over(arr, body2)


def body3(i: int, s: str, x: str = 'default'):
    print(i, s, x)

parallelize_over(range(10), body3, 'hi', x='not')


def body4(joined: tuple[int, int]):
    print(*joined)

from itertools import product
parallelize_over(list(product(range(3), range(5))), body4)
