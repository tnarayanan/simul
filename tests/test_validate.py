import simul
from simul.function import validate

import pytest


def test_detect_elem_arg_missing():
    def foo() -> int:
        return 0

    with pytest.raises(ValueError):
        validate(foo)

def test_detect_nonlocal_assign():
    x: int = 0

    def bar(i: int):
        nonlocal x
        x = i

    with pytest.raises(ValueError):
        validate(bar)

def test_detect_nonlocal_augassign():
    x: int = 0

    def bar(i: int):
        nonlocal x
        x += i

    with pytest.raises(ValueError):
        validate(bar)

def test_ok_local_assign():
    def bar(i: int):
        x = i
        return x

    validate(bar)

def test_detect_arg_assign():
    def bar(i: int, v: list):
        v = []
        return i, v

    with pytest.raises(ValueError):
        validate(bar)

def test_detect_arg_assign_property():
    class Foo:
        def __init__(self, x: int):
            self.x = x

    def bar(i: int, f: Foo):
        f.x = i
        
    with pytest.raises(ValueError):
        validate(bar)

def test_over_validates_function():
    def bar(i: int, v: list[int]):
        v = []
        return i + sum(v)
    
    with pytest.raises(ValueError):
        simul.over(range(10), bar).reduce()
