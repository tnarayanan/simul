import timeit

from itertools import product

from typing import Any, Literal, Sequence

import simul
from simul.executor import SerialExecutor
from simul.over import _over_with_executor
from simul.function import ParallelFunction


def _assert_equal_to_serial[ElemT, ReturnT](op: Literal['reduce'] | Literal['to_map'] | Literal['to_list'],
                                            seq: Sequence[ElemT],
                                            body: ParallelFunction[ElemT, ReturnT],
                                            *args: Any,
                                            **kwargs: Any):
    parallel = simul.over(seq, body, *args, **kwargs)
    serial = _over_with_executor(SerialExecutor, seq, body, *args, **kwargs)

    match op:
        case 'reduce':
            assert parallel.reduce() == serial.reduce()
        case 'to_map':
            assert parallel.to_map() == serial.to_map()
        case 'to_list':
            assert parallel.to_list() == serial.to_list()


def test_reduce_over_int():
    def body(i: int) -> int:
        return i * 2
    
    seq = range(10)
    _assert_equal_to_serial('reduce', seq, body)

def test_map_over_str():
    def body(s: str) -> str:
        return s[::-1]

    seq = ["hi", "bye"]
    _assert_equal_to_serial('to_map', seq, body)

def test_fn_with_extra_args():
    def body(i: int, s: str, x: str = 'default'):
        return i + len(s) + len(x)

    seq = range(10)
    _assert_equal_to_serial('reduce', seq, body, 'hi', x = 'not')

def test_tuple_iterable():
    def body(elem: tuple[int, int]):
        return sum(elem)
    
    seq = list(product(range(3), range(5)))
    _assert_equal_to_serial('reduce', seq, body)

def test_batch_size():
    def body(i: int) -> int:
        return i

    seq = range(int(1e6))
    seq_sum = sum(seq)

    def run_with_batch_size(batch_size: int):
        assert simul.over(seq, body).with_batch_size(batch_size).reduce() == seq_sum

    small_batch_time = timeit.timeit(lambda: run_with_batch_size(10), number=1)
    large_batch_time = timeit.timeit(lambda: run_with_batch_size(10000), number=1)

    assert small_batch_time > large_batch_time
    
