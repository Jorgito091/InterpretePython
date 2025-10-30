import ast
import operator
from typing import Any, Dict, List, Optional

# Ejemplos reducidos u opcionales (puedes mantener los tuyos)
ejemplos = [
    "a = 10\nb = 5\na + b",
    "x = 7\ny = 3\nx * y",
    "print('Hola mundo')",
    "numeros = [1,2,3,4,5]\nsum(numeros)",
    "persona = {'nombre': 'Jorge', 'edad': 25}\npersona['nombre']",
    "x = 10\nif x > 5:\n    y = 'Mayor'\nelse:\n    y = 'Menor'\ny",
    "suma = 0\nfor i in range(5):\n    suma += i\nsuma",
    "def cuadrado(n):\n    return n * n\ncuadrado(6)",
    "a = True\nb = False\na and b",
    "5 > 3 and 2 < 4",
    "lista = [10, 20, 30]\nlista[1]"
]

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

class PythonInterpreter:
    def __init__(self, max_loop_iterations: int = 100000, max_recursion_depth: int = 1000):
        # stack of scopes: each scope is a dict. Global scope is scopes[0]
        self.scopes: List[Dict[str, Any]] = [{}]
        self.functions: Dict[str, Any] = {}
        self.builtin_functions = {
            'print': self._builtin_print,
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'type': type,
            'abs': abs,
            'max': max,
            'min': min,
            'sum': sum,
            'range': range,
            'list': list,
            'dict': dict,
            'set': set,
            'tuple': tuple,
        }

        self.binary_ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.FloorDiv: operator.floordiv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,
            ast.LShift: operator.lshift,
            ast.RShift: operator.rshift,
            ast.BitOr: operator.or_,
            ast.BitXor: operator.xor,
            ast.BitAnd: operator.and_,
        }

        self.compare_ops = {
            ast.Eq: operator.eq,
            ast.NotEq: operator.ne,
            ast.Lt: operator.lt,
            ast.LtE: operator.le,
            ast.Gt: operator.gt,
            ast.GtE: operator.ge,
            ast.Is: operator.is_,
            ast.IsNot: operator.is_not,
            ast.In: lambda x, y: x in y,
            ast.NotIn: lambda x, y: x not in y,
        }

        self.unary_ops = {
            ast.UAdd: operator.pos,
            ast.USub: operator.neg,
            ast.Not: operator.not_,
            ast.Invert: operator.invert,
        }

        self.bool_ops = {
            ast.And: lambda x, y: x and y,
            ast.Or: lambda x, y: x or y,
        }

        # protections and limits
        self.max_loop_iterations = max_loop_iterations
        self.max_recursion_depth = max_recursion_depth
        self._recursion_depth = 0

    # ---------- Utilities for scopes ----------
    def _get_from_scopes(self, name: str):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        if name in self.builtin_functions:
            return self.builtin_functions[name]
        if name in self.functions:
            return self.functions[name]
        raise NameError(f"Variable o función '{name}' no definida")

    def _set_in_current_scope(self, name: str, value: Any):
        self.scopes[-1][name] = value

    # ---------- Builtins ----------
    def _builtin_print(self, *args, **kwargs):
        sep = kwargs.get('sep', ' ')
        end = kwargs.get('end', '\n')
        output = sep.join(str(arg) for arg in args) + end
        print(output, end='')
        return None

    # ---------- Public interface ----------
    def interpret(self, code: str) -> Any:
        try:
            tree = ast.parse(code, mode='exec')
            return self.visit(tree)
        except SyntaxError as e:
            return f"Error de sintaxis: {e}"
        except Exception as e:
            return f"Error de ejecución: {e}"

    # ---------- Generic visitor ----------
    def visit(self, node: ast.AST) -> Any:
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node: ast.AST) -> Any:
        raise NotImplementedError(f"Nodo {type(node).__name__} no implementado")

    # ---------- Node visitors ----------
    def visit_Module(self, node: ast.Module) -> Any:
        result = None
        for stmt in node.body:
            result = self.visit(stmt)
        return result

    def visit_Expr(self, node: ast.Expr) -> Any:
        return self.visit(node.value)

    def visit_Constant(self, node: ast.Constant) -> Any:
        return node.value

    def visit_Name(self, node: ast.Name) -> Any:
        # Distinguish between load/store contexts if needed
        if isinstance(node.ctx, ast.Store):
            return node.id
        return self._get_from_scopes(node.id)

    def visit_List(self, node: ast.List) -> List[Any]:
        return [self.visit(e) for e in node.elts]

    def visit_Tuple(self, node: ast.Tuple) -> tuple:
        return tuple(self.visit(e) for e in node.elts)

    def visit_Dict(self, node: ast.Dict) -> Dict[Any, Any]:
        result = {}
        for k_node, v_node in zip(node.keys, node.values):
            k = self.visit(k_node) if k_node is not None else None
            v = self.visit(v_node)
            result[k] = v
        return result

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = self.binary_ops[type(node.op)]
        return op(left, right)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        operand = self.visit(node.operand)
        op = self.unary_ops[type(node.op)]
        return op(operand)

    def visit_Compare(self, node: ast.Compare) -> Any:
        left = self.visit(node.left)
        for op, comp in zip(node.ops, node.comparators):
            right = self.visit(comp)
            op_func = self.compare_ops[type(op)]
            if not op_func(left, right):
                return False
            left = right
        return True

    def visit_BoolOp(self, node: ast.BoolOp) -> Any:
        if isinstance(node.op, ast.And):
            result = True
            for v in node.values:
                val = self.visit(v)
                if not val:
                    return val
                result = val
            return result
        elif isinstance(node.op, ast.Or):
            result = False
            for v in node.values:
                val = self.visit(v)
                if val:
                    return val
                result = val
            return result
        else:
            raise NotImplementedError("Operador booleano no soportado")

    # ---------- Attribute, Subscript, Slice ----------
    def visit_Attribute(self, node: ast.Attribute) -> Any:
        value = self.visit(node.value)
        if node.attr == '__dict__' and isinstance(node.ctx, ast.Store):
            # raro caso: evitar escribir directamente
            pass
        try:
            return getattr(value, node.attr)
        except Exception as e:
            raise AttributeError(f"Error al obtener atributo '{node.attr}': {e}")

    def _eval_slice_node(self, node):
        # node puede ser ast.Slice, ast.Constant, ast.Index (antiguo) o expresión
        if isinstance(node, ast.Slice):
            lower = self.visit(node.lower) if node.lower else None
            upper = self.visit(node.upper) if node.upper else None
            step = self.visit(node.step) if node.step else None
            return slice(lower, upper, step)
        # compatibilidad con versiones antiguas de ast (Index)
        if hasattr(ast, 'Index') and isinstance(node, ast.Index):
            return self.visit(node.value)
        # si es simple expresión
        return self.visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> Any:
        value = self.visit(node.value)
        slice_obj = self._eval_slice_node(node.slice)
        return value[slice_obj]

    # ---------- Assign / AugAssign ----------
    def _assign_target(self, target: ast.AST, value: Any):
        if isinstance(target, ast.Name):
            self._set_in_current_scope(target.id, value)
        elif isinstance(target, ast.Tuple) or isinstance(target, ast.List):
            # desempacar
            vals = list(value)
            if len(vals) != len(target.elts):
                raise ValueError("Desempaquetado con distinta longitud")
            for t, v in zip(target.elts, vals):
                self._assign_target(t, v)
        elif isinstance(target, ast.Subscript):
            obj = self.visit(target.value)
            idx = self._eval_slice_node(target.slice)
            obj[idx] = value
        elif isinstance(target, ast.Attribute):
            obj = self.visit(target.value)
            setattr(obj, target.attr, value)
        else:
            raise NotImplementedError(f"Asignación a target {type(target).__name__} no soportada")

    def visit_Assign(self, node: ast.Assign) -> Any:
        value = self.visit(node.value)
        for target in node.targets:
            self._assign_target(target, value)
        return value

    def visit_AugAssign(self, node: ast.AugAssign) -> Any:
        # obtener valor actual del target
        if isinstance(node.target, ast.Name):
            cur = self._get_from_scopes(node.target.id)
        elif isinstance(node.target, ast.Subscript):
            obj = self.visit(node.target.value)
            idx = self._eval_slice_node(node.target.slice)
            cur = obj[idx]
        else:
            raise NotImplementedError("AugAssign para este target no implementado")
        value = self.visit(node.value)
        op = self.binary_ops[type(node.op)]
        result = op(cur, value)
        self._assign_target(node.target, result)
        return result

    # ---------- Control flow ----------
    def visit_If(self, node: ast.If) -> Any:
        test = self.visit(node.test)
        if test:
            result = None
            for stmt in node.body:
                result = self.visit(stmt)
            return result
        else:
            result = None
            for stmt in node.orelse:
                result = self.visit(stmt)
            return result

    def visit_While(self, node: ast.While) -> Any:
        result = None
        iterations = 0
        while self.visit(node.test):
            iterations += 1
            if iterations > self.max_loop_iterations:
                raise RuntimeError("Límite de iteraciones alcanzado en while")
            for stmt in node.body:
                result = self.visit(stmt)
        return result

    def visit_For(self, node: ast.For) -> Any:
        result = None
        iterable = self.visit(node.iter)
        iterations = 0
        for item in iterable:
            iterations += 1
            if iterations > self.max_loop_iterations:
                raise RuntimeError("Límite de iteraciones alcanzado en for")
            if isinstance(node.target, ast.Name):
                self._set_in_current_scope(node.target.id, item)
            else:
                self._assign_target(node.target, item)
            for stmt in node.body:
                result = self.visit(stmt)
        return result

    # ---------- Functions ----------
    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        # Capturar scopes actuales como closure
        closure_scopes = [dict(s) for s in self.scopes]

        def user_function(*args, **kwargs):
            if self._recursion_depth > self.max_recursion_depth:
                raise RecursionError("Profundidad máxima de recursión alcanzada")
            self._recursion_depth += 1
            old_scopes = self.scopes
            # nuevo stack: closure scopes (copias) + nuevos locals al final
            local_scope: Dict[str, Any] = {}
            self.scopes = closure_scopes + [local_scope]

            # args.positional
            arg_names = [a.arg for a in node.args.args]
            # defaults: aligned to last N positional args
            defaults = [self.visit(d) for d in node.args.defaults] if node.args.defaults else []
            num_non_default = len(arg_names) - len(defaults)
            # asignar posicionales
            for i, name in enumerate(arg_names):
                if i < len(args):
                    local_scope[name] = args[i]
                else:
                    # default si corresponde
                    if i >= num_non_default:
                        local_scope[name] = defaults[i - num_non_default]
                    else:
                        local_scope[name] = None

            # varargs
            if node.args.vararg:
                local_scope[node.args.vararg.arg] = tuple(args[len(arg_names):])
            # keyword-only args
            kwonly_names = [a.arg for a in node.args.kwonlyargs]
            kw_defaults = [self.visit(d) if d is not None else None for d in getattr(node.args, "kw_defaults", [])]
            for i, name in enumerate(kwonly_names):
                if name in kwargs:
                    local_scope[name] = kwargs.pop(name)
                else:
                    default_val = kw_defaults[i] if i < len(kw_defaults) else None
                    local_scope[name] = default_val

            # kwargs (catch-all)
            if node.args.kwarg:
                local_scope[node.args.kwarg.arg] = kwargs
            else:
                # si quedan kwargs inesperados, lanzamos TypeError como Python real
                if kwargs:
                    raise TypeError(f"{node.name}() got unexpected keyword arguments {list(kwargs.keys())}")

            # Ejecutar cuerpo
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

        # marcar función para identificación
        user_function._is_user_func = True  # type: ignore
        user_function._ast_node = node  # type: ignore
        self.functions[node.name] = user_function
        # también exponer en el scope global
        self._set_in_current_scope(node.name, user_function)
        return user_function

    def visit_Return(self, node: ast.Return) -> Any:
        value = self.visit(node.value) if node.value else None
        raise ReturnValue(value)

    # ---------- Calls ----------
    def visit_Call(self, node: ast.Call) -> Any:
        func = self.visit(node.func)
        args = [self.visit(a) for a in node.args]
        kwargs = {kw.arg: self.visit(kw.value) for kw in node.keywords if kw.arg is not None}
        # soportar llamadas a funciones definidas por el intérprete y builtins
        if hasattr(func, "_is_user_func") and getattr(func, "_is_user_func"):
            return func(*args, **kwargs)
        if callable(func):
            return func(*args, **kwargs)
        raise TypeError(f"'{func}' no es una función")

# ---------- Runner / REPL ----------
def run_interpreter():
    interpreter = PythonInterpreter()
    print("Intérprete mejorado de Python (simplificado)")
    print("Escribe 'exit()' para salir")
    print("-" * 30)
    while True:
        try:
            code = input(">>> ")
            if code.strip() == "exit()":
                break
            if not code.strip():
                continue
            # permitir multi-line básico: si termina en ':' pedir más líneas
            # (muy simple, no robusto)
            if code.rstrip().endswith(':'):
                lines = [code]
                while True:
                    nxt = input("... ")
                    if not nxt:
                        break
                    lines.append(nxt)
                    if not nxt.rstrip().endswith(':'):
                        # no detectamos estructura completa, pero aceptamos entrada
                        pass
                code = "\n".join(lines)
            result = interpreter.interpret(code)
            if result is not None:
                print(repr(result))
        except KeyboardInterrupt:
            print("\nSaliendo...")
            break
        except EOFError:
            break

if __name__ == "__main__":
    import sys
    interpreter = PythonInterpreter()

    if len(sys.argv) > 1:
        filename = sys.argv[1]
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                code = f.read()
            print(f"Ejecutando archivo: {filename}\n" + "-"*30)
            result = interpreter.interpret(code)
            if result is not None:
                print(f"Resultado: {result}")
        except Exception as e:
            print(f"Error al ejecutar el archivo: {e}")
    else:
        print("=== Ejecutando ejemplos ===")
        for i, codigo in enumerate(ejemplos, 1):
            print(f"\nEjemplo {i}:")
            print(f"Código: {codigo.strip()}")
            print("Salida:")
            result = interpreter.interpret(codigo)
            if result is not None:
                print(f"Resultado: {result}")

        print("\n" + "="*50)
        print("Para usar el intérprete interactivo, ejecuta:")
        print("run_interpreter()")