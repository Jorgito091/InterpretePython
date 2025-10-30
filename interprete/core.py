# core.py
import ast
import operator
from typing import Any, Dict, List
from .builtins import BUILTIN_FUNCS

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

class PythonInterpreter:
    def __init__(self, max_loop_iterations=100000, max_recursion_depth=1000):
        self.scopes: List[Dict[str, Any]] = [{}]
        self.functions: Dict[str, Any] = {}
        self.builtin_functions = BUILTIN_FUNCS
        self._recursion_depth = 0
        self.max_loop_iterations = max_loop_iterations
        self.max_recursion_depth = max_recursion_depth

        self._init_ops()

    def _init_ops(self):
        self.binary_ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.FloorDiv: operator.floordiv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,
        }
        self.compare_ops = {
            ast.Eq: operator.eq,
            ast.NotEq: operator.ne,
            ast.Lt: operator.lt,
            ast.LtE: operator.le,
            ast.Gt: operator.gt,
            ast.GtE: operator.ge,
        }
        self.unary_ops = {
            ast.UAdd: operator.pos,
            ast.USub: operator.neg,
            ast.Not: operator.not_,
        }
        self.bool_ops = {
            ast.And: lambda x, y: x and y,
            ast.Or: lambda x, y: x or y,
        }

    def _get_from_scopes(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        if name in self.builtin_functions:
            return self.builtin_functions[name]
        if name in self.functions:
            return self.functions[name]
        raise NameError(f"Variable o función '{name}' no definida")

    def _set_in_current_scope(self, name, value):
        self.scopes[-1][name] = value

    def debug_methods(self):
        print("Métodos disponibles:", [m for m in dir(self) if not m.startswith("_")])