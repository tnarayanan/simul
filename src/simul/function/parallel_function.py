from typing import Any, Protocol


class ParallelFunction[ElemT, ReturnT](Protocol):
    def __call__(self, __item: ElemT, *args: Any, **kwargs: Any) -> ReturnT: ...
