import ast
import operator
import sys
from typing import Any, Dict, List, Optional

        # Lista de ejemplos de código
ejemplos = [
    # Operaciones básicas
    "a = 10\nb = 5\na + b",
    "x = 7\ny = 3\nx * y",
            
    # Uso de print
    "print('Hola mundo')",
            
    # Listas y sumas
    "numeros = [1,2,3,4,5]\nsum(numeros)",
        
    # Diccionarios
    "persona = {'nombre': 'Jorge', 'edad': 25}\npersona['nombre']",
            
    # Condicionales
    "x = 10\nif x > 5:\n    y = 'Mayor'\nelse:\n    y = 'Menor'\ny",
            
    # Bucles
    "suma = 0\nfor i in range(5):\n    suma += i\nsuma",
            
    # Funciones
    "def cuadrado(n):\n    return n * n\ncuadrado(6)",
            
    # Booleanos
    "a = True\nb = False\na and b",
            
    # Comparaciones
    "5 > 3 and 2 < 4",
            
    # Acceso a listas
    "lista = [10, 20, 30]\nlista[1]"
    ]
class PythonInterpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}
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
        
        # Operadores binarios
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
        
        
        # Operadores de comparación
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
        
        # Operadores unarios
        self.unary_ops = {
            ast.UAdd: operator.pos,
            ast.USub: operator.neg,
            ast.Not: operator.not_,
            ast.Invert: operator.invert,
        }
        
        # Operadores booleanos
        self.bool_ops = {
            ast.And: lambda x, y: x and y,
            ast.Or: lambda x, y: x or y,
        }

    def _builtin_print(self, *args, **kwargs):
        """Función print personalizada"""
        sep = kwargs.get('sep', ' ')
        end = kwargs.get('end', '\n')
        output = sep.join(str(arg) for arg in args) + end
        print(output, end='')
        return None

    def interpret(self, code: str) -> Any:
        """Interpreta código Python"""
        try:
            tree = ast.parse(code, mode='exec')
            return self.visit(tree)
        except SyntaxError as e:
            return f"Error de sintaxis: {e}"
        except Exception as e:
            return f"Error de ejecución: {e}"

    def visit(self, node: ast.AST) -> Any:
        """Visita un nodo del AST"""
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node: ast.AST) -> Any:
        """Método genérico para nodos no implementados"""
        raise NotImplementedError(f"Nodo {type(node).__name__} no implementado")

    # Visitadores para diferentes tipos de nodos
    
    def visit_Module(self, node: ast.Module) -> Any:
        """Visita el módulo principal"""
        result = None
        for stmt in node.body:
            result = self.visit(stmt)
        return result

    def visit_Expr(self, node: ast.Expr) -> Any:
        """Visita una expresión"""
        return self.visit(node.value)

    def visit_Assign(self, node: ast.Assign) -> Any:
        """Maneja asignaciones"""
        value = self.visit(node.value)
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables[target.id] = value
            else:
                raise NotImplementedError("Solo se soportan asignaciones simples")
        return value

    def visit_AugAssign(self, node: ast.AugAssign) -> Any:
        """Maneja asignaciones aumentadas (+=, -=, etc.)"""
        target_value = self.visit(node.target)
        value = self.visit(node.value)
        op = self.binary_ops[type(node.op)]
        result = op(target_value, value)
        
        if isinstance(node.target, ast.Name):
            self.variables[node.target.id] = result
        else:
            raise NotImplementedError("Solo se soportan asignaciones aumentadas simples")
        return result

    def visit_Name(self, node: ast.Name) -> Any:
        """Visita nombres de variables"""
        if node.id in self.variables:
            return self.variables[node.id]
        elif node.id in self.builtin_functions:
            return self.builtin_functions[node.id]
        elif node.id in self.functions:
            return self.functions[node.id]
        else:
            raise NameError(f"Variable '{node.id}' no definida")

    def visit_Constant(self, node: ast.Constant) -> Any:
        """Visita constantes (números, strings, etc.)"""
        return node.value

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        """Maneja operaciones binarias"""
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = self.binary_ops[type(node.op)]
        return op(left, right)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        """Maneja operaciones unarias"""
        operand = self.visit(node.operand)
        op = self.unary_ops[type(node.op)]
        return op(operand)

    def visit_Compare(self, node: ast.Compare) -> Any:
        """Maneja comparaciones"""
        left = self.visit(node.left)
        for op, comparator in zip(node.ops, node.comparators):
            right = self.visit(comparator)
            op_func = self.compare_ops[type(op)]
            if not op_func(left, right):
                return False
            left = right
        return True

    def visit_BoolOp(self, node: ast.BoolOp) -> Any:
        """Maneja operaciones booleanas (and, or)"""
        op_func = self.bool_ops[type(node.op)]
        result = self.visit(node.values[0])
        
        for value in node.values[1:]:
            if isinstance(node.op, ast.And) and not result:
                return result
            elif isinstance(node.op, ast.Or) and result:
                return result
            result = op_func(result, self.visit(value))
        
        return result

    def visit_Call(self, node: ast.Call) -> Any:
        """Maneja llamadas a funciones"""
        func = self.visit(node.func)
        args = [self.visit(arg) for arg in node.args]
        kwargs = {kw.arg: self.visit(kw.value) for kw in node.keywords}
        
        if callable(func):
            return func(*args, **kwargs)
        else:
            raise TypeError(f"'{func}' no es una función")

    def visit_If(self, node: ast.If) -> Any:
        """Maneja estructuras if-elif-else"""
        test = self.visit(node.test)
        if test:
            result = None
            for stmt in node.body:
                result = self.visit(stmt)
            return result
        elif node.orelse:
            result = None
            for stmt in node.orelse:
                result = self.visit(stmt)
            return result
        return None

    def visit_While(self, node: ast.While) -> Any:
        """Maneja bucles while"""
        result = None
        while self.visit(node.test):
            for stmt in node.body:
                result = self.visit(stmt)
        return result

    def visit_For(self, node: ast.For) -> Any:
        """Maneja bucles for"""
        result = None
        iterable = self.visit(node.iter)
        
        for item in iterable:
            if isinstance(node.target, ast.Name):
                self.variables[node.target.id] = item
            for stmt in node.body:
                result = self.visit(stmt)
        return result

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        """Define funciones"""
        def user_function(*args, **kwargs):
            # Crear nuevo contexto para la función
            old_vars = self.variables.copy()
            
            # Asignar argumentos
            for i, arg in enumerate(node.args.args):
                if i < len(args):
                    self.variables[arg.arg] = args[i]
                else:
                    # Manejar argumentos por defecto si los hay
                    self.variables[arg.arg] = None
            
            # Ejecutar cuerpo de la función
            result = None
            try:
                for stmt in node.body:
                    result = self.visit(stmt)
            except ReturnValue as ret:
                result = ret.value
            finally:
                # Restaurar contexto anterior
                self.variables = old_vars
            
            return result
        
        self.functions[node.name] = user_function
        return user_function

    def visit_Return(self, node: ast.Return) -> Any:
        """Maneja declaraciones return"""
        value = self.visit(node.value) if node.value else None
        raise ReturnValue(value)

    def visit_List(self, node: ast.List) -> List[Any]:
        """Maneja listas"""
        return [self.visit(item) for item in node.elts]

    def visit_Dict(self, node: ast.Dict) -> Dict[Any, Any]:
        """Maneja diccionarios"""
        result = {}
        for key, value in zip(node.keys, node.values):
            k = self.visit(key)
            v = self.visit(value)
            result[k] = v
        return result

    def visit_Subscript(self, node: ast.Subscript) -> Any:
        """Maneja acceso por índice o slice"""
        value = self.visit(node.value)
        slice_value = self.visit(node.slice)
        return value[slice_value]

class ReturnValue(Exception):
    """Excepción para manejar return en funciones"""
    def __init__(self, value):
        self.value = value

# Función principal para usar el intérprete
def run_interpreter():
    """Ejecuta el intérprete en modo interactivo"""
    interpreter = PythonInterpreter()
    print("Intérprete básico de Python")
    print("Escribe 'exit()' para salir")
    print("-" * 30)
    
    while True:
        try:
            code = input(">>> ")
            if code.strip() == "exit()":
                break
            elif code.strip():
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
