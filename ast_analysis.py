import inspect
import ast

def foo(x: int):
    a = 3
    b = [0 for _ in range(x)]
    for i in range(x):
        a = i * i
        b[i] = i * i
    return a

def sample_function(x):
    return x * x + 2 * x + 1

tree = ast.parse(inspect.getsource(foo))
print(ast.dump(tree, indent=4))
