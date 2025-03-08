import ast
import inspect
import textwrap

from functools import wraps

from simul.analyze.visitor import LoopDependencyDetector


def analyze(fn):
    has_analyzed = False

    @wraps(fn)
    def wrapper(*args, **kwargs):
        nonlocal has_analyzed

        if not has_analyzed:
            # do analysis
            source = textwrap.dedent(inspect.getsource(fn))
            print(source)
            tree = ast.parse(source)
            print(ast.dump(tree, indent=4))

            LoopDependencyDetector().visit(tree)
            
            print("finished analysis")
            has_analyzed = True
        return fn(*args, **kwargs)

    return wrapper


