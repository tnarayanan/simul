import ast


class LoopDependencyDetector(ast.NodeVisitor):
    def __init__(self):
        self.unpermitted_writes: set[str] = set()

    def _get_name_from(self, node: ast.Name | ast.Attribute) -> str | None:
        match node:
            case ast.Name(id=id):
                return id
            case ast.Attribute(value=value):
                if isinstance(value, (ast.Name, ast.Attribute)):
                    return self._get_name_from(value)
                return None

    def visit_Module(self, node: ast.Module):
        for stmt in node.body:
            self.visit(stmt)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        print(node.name)
        if len(node.args.args) == 0:
            raise ValueError("Function targets for parallelize require at least one argument")

        # writing to any argument other than the current element is not permitted
        for arg in node.args.args[1:]:
            self.unpermitted_writes.add(arg.arg)

        for stmt in node.body:
            self.visit(stmt)

    def visit_Nonlocal(self, node: ast.Nonlocal):
        self.unpermitted_writes.update(node.names)

    def visit_Global(self, node: ast.Global):
        self.unpermitted_writes.update(node.names)

    def visit_Assign(self, node: ast.Assign):
        for target in node.targets:
            if isinstance(target, (ast.Name, ast.Attribute)):
                if self._get_name_from(target) in self.unpermitted_writes:
                    raise ValueError(f"Write to non-local value on line {node.lineno}")

    def visit_AugAssign(self, node: ast.AugAssign):
        if isinstance(node.target, (ast.Name, ast.Attribute)):
            if self._get_name_from(node.target) in self.unpermitted_writes:
                raise ValueError(f"Write to non-local value on line {node.lineno}")

