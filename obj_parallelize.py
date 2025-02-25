import queue
import threading
import timeit

from itertools import product
from typing import Any, Generic, Optional, Protocol, Sequence, TypeVar

T = TypeVar('T', contravariant=True)
S = TypeVar('S', contravariant=True)

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

    def _run(self, worker, work_queue: queue.Queue[Optional[Sequence[T]]]) -> None:
        self.batch_size = self._get_batch_size_from_attrs()
        threads: list[threading.Thread] = []

        for _ in range(12):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        n = len(self.seq)
        for start in range(0, n, self.batch_size):
            end = min(n, start + self.batch_size)
            work_queue.put(self.seq[start:end])
        for _ in threads:
            # thread terminators
            work_queue.put(None)

        work_queue.join()
        for thread in threads:
            thread.join()

    def map(self) -> dict[T, S]:
        work_queue: queue.Queue[Optional[Sequence[T]]] = queue.Queue()

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
                    output[i] = self.fn(i, *self.args, **self.kwargs)
                work_queue.task_done()

        self._run(worker, work_queue)

        return output


def body1(i: int):
    print(i)

ParallelizeOver(range(10)).exec(body1).map()


def body2(s: str):
    print(s)
    return s[::-1]

arr = ['hi', 'bye']
print(ParallelizeOver(arr).exec(body2).map())


def body3(i: int, s: str, x: str = 'default'):
    print(i, s, x)

ParallelizeOver(range(10)).exec(body3, 'hi', x='not').map()


def body4(joined: tuple[int, int]):
    print(*joined)

ParallelizeOver(list(product(range(3), range(5)))).exec(body4).map()


def body5(i: int):
    _ = 10 ** 4

def run5():
    ParallelizeOver(range(int(1e7))).with_batch_size(100).exec(body5).map()

def run6():
    ParallelizeOver(range(int(1e7))).with_batch_size(10000).exec(body5).map()

print(f"Exec time: {timeit.timeit(run5, number=1)}")
print(f"Exec time: {timeit.timeit(run6, number=1)}")

    

def body(i: int):
    _ = 10 ** 3 + i
ParallelizeOver(range(10)).exec(body).map()

