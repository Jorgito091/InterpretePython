# nodes.py
import ast
from .core import PythonInterpreter, ReturnValue

class NodeVisitors(PythonInterpreter):
    def interpret(self, source: str):
        tree = ast.parse(source)
        return self.visit(tree)

    def visit(self, node):
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"Nodo {node.__class__.__name__} no implementado")

    # ---------- Soporte básico ----------
    def visit_Pass(self, node):
        return None

    def visit_Module(self, node):
        result = None
        for stmt in node.body:
            result = self.visit(stmt)
        return result

    def visit_Expr(self, node):
        return self.visit(node.value)

    def visit_Constant(self, node):
        return node.value

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            return self._get_from_scopes(node.id)
        return node.id

    def visit_List(self, node):
        return [self.visit(e) for e in node.elts]

    def visit_Tuple(self, node):
        return tuple(self.visit(e) for e in node.elts)

    def visit_Dict(self, node):
        return {self.visit(k): self.visit(v) for k, v in zip(node.keys, node.values)}

    # ---------- Asignaciones ----------
    def _assign_target(self, target, value):
        if isinstance(target, ast.Name):
            self._set_in_current_scope(target.id, value)
        elif isinstance(target, (ast.Tuple, ast.List)):
            vals = list(value)
            if len(vals) != len(target.elts):
                raise ValueError("Desempaquetado con distinta longitud")
            for t, v in zip(target.elts, vals):
                self._assign_target(t, v)
        elif isinstance(target, ast.Subscript):
            obj = self.visit(target.value)
            idx = self.visit(target.slice)
            obj[idx] = value
        elif isinstance(target, ast.Attribute):
            obj = self.visit(target.value)
            setattr(obj, target.attr, value)
        else:
            raise NotImplementedError(f"Asignación a target {type(target).__name__} no soportada")

    def visit_Assign(self, node):
        value = self.visit(node.value)
        for target in node.targets:
            self._assign_target(target, value)
        return value

    # ---------- Operadores ----------
    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        return self.binary_ops[type(node.op)](left, right)

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        return self.unary_ops[type(node.op)](operand)

    def visit_Compare(self, node):
        left = self.visit(node.left)
        for op, comparator in zip(node.ops, node.comparators):
            right = self.visit(comparator)
            if not self.compare_ops[type(op)](left, right):
                return False
            left = right
        return True

    def visit_BoolOp(self, node):
        values = [self.visit(v) for v in node.values]
        result = values[0]
        for val in values[1:]:
            result = self.bool_ops[type(node.op)](result, val)
        return result

    # ---------- Control de flujo ----------
    def visit_If(self, node):
        if self.visit(node.test):
            for stmt in node.body:
                self.visit(stmt)
        else:
            for stmt in node.orelse:
                self.visit(stmt)

    def visit_While(self, node):
        count = 0
        while self.visit(node.test):
            for stmt in node.body:
                self.visit(stmt)
            count += 1
            if count > self.max_loop_iterations:
                raise RuntimeError("Límite de iteraciones alcanzado en while")

    def visit_For(self, node):
        iterable = self.visit(node.iter)
        for val in iterable:
            self._assign_target(node.target, val)
            for stmt in node.body:
                self.visit(stmt)

    # ---------- Funciones ----------
    def visit_FunctionDef(self, node):
        closure_scopes = [dict(s) for s in self.scopes]

        def user_func(*args, **kwargs):
            if self._recursion_depth > self.max_recursion_depth:
                raise RecursionError("Profundidad máxima de recursión alcanzada")
            self._recursion_depth += 1
            old_scopes = self.scopes
            local_scope = {}
            self.scopes = closure_scopes + [local_scope]

            arg_names = [a.arg for a in node.args.args]
            defaults = [self.visit(d) for d in node.args.defaults] if node.args.defaults else []
            num_non_default = len(arg_names) - len(defaults)
            for i, name in enumerate(arg_names):
                if i < len(args):
                    local_scope[name] = args[i]
                else:
                    local_scope[name] = defaults[i - num_non_default] if i >= num_non_default else None

            if node.args.vararg:
                local_scope[node.args.vararg.arg] = tuple(args[len(arg_names):])

            kwonly_names = [a.arg for a in node.args.kwonlyargs]
            kw_defaults = [self.visit(d) if d else None for d in getattr(node.args, "kw_defaults", [])]
            for i, name in enumerate(kwonly_names):
                if name in kwargs:
                    local_scope[name] = kwargs.pop(name)
                else:
                    default_val = kw_defaults[i] if i < len(kw_defaults) else None
                    local_scope[name] = default_val

            if node.args.kwarg:
                local_scope[node.args.kwarg.arg] = kwargs
            elif kwargs:
                raise TypeError(f"{node.name}() got unexpected keyword arguments {list(kwargs.keys())}")

            result = None
            try:
                for stmt in node.body:
                    result = self.visit(stmt)
            except ReturnValue as ret:
                result = ret.value
            finally:
                self.scopes = old_scopes
                self._recursion_depth -= 1
            return result

        user_func._is_user_func = True
        self.functions[node.name] = user_func
        self._set_in_current_scope(node.name, user_func)
        return user_func

    def visit_Return(self, node):
        value = self.visit(node.value) if node.value else None
        raise ReturnValue(value)

    # ---------- Llamadas ----------
    def visit_Call(self, node):
        func = self.visit(node.func)
        args = [self.visit(a) for a in node.args]
        kwargs = {kw.arg: self.visit(kw.value) for kw in node.keywords if kw.arg is not None}
        if hasattr(func, "_is_user_func") and getattr(func, "_is_user_func"):
            return func(*args, **kwargs)
        if callable(func):
            return func(*args, **kwargs)
        raise TypeError(f"'{func}' no es callable")

    def visit_Attribute(self, node):
        value = self.visit(node.value)
        return getattr(value, node.attr)

    def visit_Subscript(self, node):
        value = self.visit(node.value)
        idx = self.visit(node.slice)
        return value[idx]

    def visit_Slice(self, node):
        lower = self.visit(node.lower) if node.lower else None
        upper = self.visit(node.upper) if node.upper else None
        step = self.visit(node.step) if node.step else None
        return slice(lower, upper, step)

    # ---------- Clases ----------
    def visit_ClassDef(self, node):
        class_scope = {}
        for stmt in node.body:
            if isinstance(stmt, ast.FunctionDef):
                func = self.visit(stmt)
                class_scope[stmt.name] = func
            elif isinstance(stmt, ast.Assign):
                value = self.visit(stmt.value)
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        class_scope[target.id] = value
                    else:
                        raise NotImplementedError("Asignación compleja en clase no soportada")
            elif isinstance(stmt, ast.Pass):
                continue
            else:
                raise NotImplementedError(f"Nodo {type(stmt).__name__} en clase no soportado")
        cls = type(node.name, (), class_scope)
        self._set_in_current_scope(node.name, cls)
        return cls

    # ---------- Nonlocal ----------
    def visit_Nonlocal(self, node):
        for name in node.names:
            if not any(name in scope for scope in self.scopes[:-1]):
                raise NameError(f"Variable nonlocal '{name}' no definida en scope externo")
        return None