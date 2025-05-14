from abc import ABC, abstractmethod
from typing import Any, Sequence

from simul.function import ParallelFunction, validate


class Executor[ElemT, ReturnT](ABC):
    def __init__(
        self,
        seq: Sequence[ElemT],
        fn: ParallelFunction[ElemT, ReturnT],
        *args: Any,
        **kwargs: Any,
    ):
        self.seq: Sequence[ElemT] = seq

        self.fn: ParallelFunction[ElemT, ReturnT] = fn
        self.args: Any = args
        self.kwargs: Any = kwargs

        validate(self.fn)

    @abstractmethod
    def to_map(self) -> dict[ElemT, ReturnT]: ...

    @abstractmethod
    def to_list(self) -> list[ReturnT]: ...

    @abstractmethod
    def reduce(self) -> ReturnT: ...
