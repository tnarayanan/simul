import queue
import threading

from typing import Any, Optional, Self, Sequence

from simul.executor import Executor
from simul.types import ParallelFunction


class ThreadPoolExecutor[ElemT, ReturnT](Executor[ElemT, ReturnT]):
    def __init__(self, seq: Sequence[ElemT], fn: ParallelFunction[ElemT, ReturnT], *args: Any, **kwargs: Any):
        super().__init__(seq, fn, *args, **kwargs)
        self.batch_size: Optional[int] = None
        self.num_batches: Optional[int] = None

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

    def with_batch_size(self, batch_size: int) -> Self:
        self.batch_size = batch_size
        return self

    def with_num_batches(self, num_batches: int) -> Self:
        self.num_batches = num_batches
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

    def to_map(self) -> dict[ElemT, ReturnT]:
        work_queue: queue.Queue[Optional[range]] = queue.Queue()

        output: dict[ElemT, ReturnT] = {}

        def worker():
            assert self.fn is not None, "Must specify function by calling exec"
            while True:
                segment = work_queue.get()
                if segment is None:
                    # terminate thread
                    work_queue.task_done()
                    break

                for i in segment:
                    elem: ElemT = self.seq[i]
                    output[elem] = self.fn(elem, *self.args, **self.kwargs)
                work_queue.task_done()

        self._run(worker, work_queue)

        return output

    def to_list(self) -> list[Optional[ReturnT]]:
        work_queue: queue.Queue[Optional[range]] = queue.Queue()

        output: list[Optional[ReturnT]] = [None for _ in range(len(self.seq))]

        def worker():
            assert self.fn is not None, "Must specify function by calling exec"
            while True:
                segment = work_queue.get()
                if segment is None:
                    # terminate thread
                    work_queue.task_done()
                    break

                for i in segment:
                    elem: ElemT = self.seq[i]
                    output[i] = self.fn(elem, *self.args, **self.kwargs)
                work_queue.task_done()

        self._run(worker, work_queue)

        return output

    def reduce(self) -> Optional[ReturnT]:
        work_queue: queue.Queue[Optional[range]] = queue.Queue()

        lock = threading.Lock()
        output: Optional[ReturnT] = None

        def worker():
            nonlocal output
            
            assert self.fn is not None, "Must specify function by calling exec"
            thread_output: Optional[ReturnT] = None
            while True:
                segment = work_queue.get()
                if segment is None:
                    # terminate thread
                    work_queue.task_done()
                    break

                for i in segment:
                    elem: ElemT = self.seq[i]
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

