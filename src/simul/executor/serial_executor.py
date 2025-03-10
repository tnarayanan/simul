from typing import Any, Sequence

from simul.executor import Executor
from simul.function import ParallelFunction


class SerialExecutor[ElemT, ReturnT](Executor[ElemT, ReturnT]):
    def __init__(self, seq: Sequence[ElemT], fn: ParallelFunction[ElemT, ReturnT], *args: Any, **kwargs: Any):
        super().__init__(seq, fn, *args, **kwargs)

    def to_map(self) -> dict[ElemT, ReturnT]:
        return {elem: self.fn(elem, *self.args, **self.kwargs) for elem in self.seq}

    def to_list(self) -> list[ReturnT]:
        return [self.fn(elem, *self.args, **self.kwargs) for elem in self.seq]

    def reduce(self) -> ReturnT:
        return sum(self.to_list())

