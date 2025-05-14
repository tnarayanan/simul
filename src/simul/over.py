from typing import Any, Sequence, Type

from simul.executor import Executor, ThreadPoolExecutor
from simul.function import ParallelFunction


def over[ElemT, ReturnT](
    seq: Sequence[ElemT],
    fn: ParallelFunction[ElemT, ReturnT],
    *args: Any,
    **kwargs: Any,
) -> ThreadPoolExecutor[ElemT, ReturnT]:
    return ThreadPoolExecutor(seq, fn, *args, **kwargs)


def _over_with_executor[ElemT, ReturnT](
    executor: Type[Executor[ElemT, ReturnT]],
    seq: Sequence[ElemT],
    fn: ParallelFunction[ElemT, ReturnT],
    *args: Any,
    **kwargs: Any,
) -> Executor[ElemT, ReturnT]:
    return executor(seq, fn, *args, **kwargs)
