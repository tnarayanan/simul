import timeit

from simul import analyze
import pytest


def test_ast_parsed_once():
    @analyze
    def foo(i: int) -> int:
        return 0

    def foo_runner():
        foo(0)

    analysis_time = timeit.timeit(foo_runner, number=1)
    num_exec = 1_000_000
    non_analysis_time = timeit.timeit(foo_runner, number=num_exec) / num_exec
    assert analysis_time > non_analysis_time

def test_detect_elem_arg_missing():
    @analyze
    def foo():
        return 0

    with pytest.raises(ValueError):
        foo()

def test_detect_nonlocal_assign():
    x: int = 0

    @analyze
    def bar(i: int):
        nonlocal x
        x = i

    with pytest.raises(ValueError):
        bar(2)

def test_detect_nonlocal_augassign():
    x: int = 0

    @analyze
    def bar(i: int):
        nonlocal x
        x += i

    with pytest.raises(ValueError):
        bar(2)

def test_ok_local_assign():
    @analyze
    def bar(i: int):
        x = i

    bar(2)

def test_detect_arg_assign():
    @analyze
    def bar(i: int, v: list):
        v = []

    with pytest.raises(ValueError):
        bar(0, [1, 2])

def test_detect_arg_assign_property():
    class Foo:
        def __init__(self, x: int):
            self.x = x

    @analyze
    def bar(i: int, f: Foo):
        f.x = i
        
    with pytest.raises(ValueError):
        bar(0, Foo(1))
