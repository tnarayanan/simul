import queue
import threading
import timeit

from itertools import product
from typing import Any, Generic, Optional, Protocol, Sequence, TypeVar

T = TypeVar('T', contravariant=True)
S = TypeVar('S', covariant=True)

class ParallelFunction[T, S](Protocol):
    def __call__(self, __item: T, *args: Any, **kwargs: Any) -> S: ...

class ParallelizeOver(Generic[T, S]):
    def __init__(self, seq: Sequence[T]):
        self.seq: Sequence[T] = seq

        self.batch_size: Optional[int] = None
        self.num_batches: Optional[int] = None

        self.fn: Optional[ParallelFunction[T, S]] = None
        self.args: Any = None
        self.kwargs: Any = None

    def _get_batch_size_from_attrs(self) -> int:
        if self.batch_size is not None and self.num_batches is not None:
            raise ValueError("cannot specify both batch_size and num_batches")
        if self.batch_size is not None and self.batch_size <= 0:
            raise ValueError("batch_size must be positive")

        if self.batch_size is not None:
            return self.batch_size
        elif self.num_batches is not None:
            return len(self.seq) // self.num_batches
        else:
            return 1

    def with_batch_size(self, batch_size: int) -> 'ParallelizeOver':
        self.batch_size = batch_size
        return self

    def with_num_batches(self, num_batches: int) -> 'ParallelizeOver':
        self.num_batches = num_batches
        return self

    def exec(self, fn: ParallelFunction[T, S], *args: Any, **kwargs: Any) -> 'ParallelizeOver':
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        
        return self

    def _run(self, worker, work_queue: queue.Queue[Optional[range]]) -> None:
        self.batch_size = self._get_batch_size_from_attrs()
        threads: list[threading.Thread] = []

        for _ in range(12):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        n = len(self.seq)
        for start in range(0, n, self.batch_size):
            end = min(n, start + self.batch_size)
            work_queue.put(range(start, end))
        for _ in threads:
            # thread terminators
            work_queue.put(None)

        work_queue.join()
        for thread in threads:
            thread.join()

    def to_map(self) -> dict[T, S]:
        work_queue: queue.Queue[Optional[range]] = queue.Queue()

        output: dict[T, S] = {}

        def worker():
            assert self.fn is not None, "Must specify function by calling exec"
            while True:
                segment = work_queue.get()
                if segment is None:
                    # terminate thread
                    work_queue.task_done()
                    break

                for i in segment:
                    elem: T = self.seq[i]
                    output[elem] = self.fn(elem, *self.args, **self.kwargs)
                work_queue.task_done()

        self._run(worker, work_queue)

        return output

    def to_list(self) -> list[S]:
        work_queue: queue.Queue[Optional[range]] = queue.Queue()

        output: list[Optional[S]] = [None for _ in range(len(self.seq))]

        def worker():
            assert self.fn is not None, "Must specify function by calling exec"
            while True:
                segment = work_queue.get()
                if segment is None:
                    # terminate thread
                    work_queue.task_done()
                    break

                for i in segment:
                    elem: T = self.seq[i]
                    output[i] = self.fn(elem, *self.args, **self.kwargs)
                work_queue.task_done()

        self._run(worker, work_queue)

        return output

    def reduce(self) -> S:
        work_queue: queue.Queue[Optional[range]] = queue.Queue()

        lock = threading.Lock()
        output: Optional[S] = None

        def worker():
            nonlocal output
            
            assert self.fn is not None, "Must specify function by calling exec"
            thread_output: Optional[S] = None
            while True:
                segment = work_queue.get()
                if segment is None:
                    # terminate thread
                    work_queue.task_done()
                    break

                for i in segment:
                    elem: T = self.seq[i]
                    cur_output = self.fn(elem, *self.args, **self.kwargs)
                    if thread_output is None:
                        thread_output = cur_output
                    else:
                        thread_output += cur_output
                work_queue.task_done()

            if thread_output is not None:
                with lock:
                    if output is None:
                        output = thread_output
                    else:
                        output += thread_output

        self._run(worker, work_queue)

        return output


def body1(i: int):
    return i * 2

print(ParallelizeOver(range(10)).exec(body1).reduce())


def body2(s: str):
    return s[::-1]

arr = ['hi', 'bye']
print(ParallelizeOver(arr).exec(body2).to_map())


def body3(i: int, s: str, x: str = 'default'):
    return i + len(s) + len(x)

print(ParallelizeOver(range(10)).exec(body3, 'hi', x='not').reduce())


def body4(joined: tuple[int, int]):
    return sum(joined)

print(ParallelizeOver(list(product(range(3), range(5)))).exec(body4).reduce())


def body5(i: int):
    return i + 10 ** 4

def run5():
    print(ParallelizeOver(range(int(1e7))).with_batch_size(100).exec(body5).reduce())

def run6():
    print(ParallelizeOver(range(int(1e7))).with_batch_size(100000).exec(body5).reduce())

print(f"Exec time: {timeit.timeit(run5, number=1)}")
print(f"Exec time: {timeit.timeit(run6, number=1)}")

    

def body(i: int):
    _ = 10 ** 3 + i
ParallelizeOver(range(10)).exec(body).to_map()

