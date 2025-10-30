# runner.py
from .nodes import NodeVisitors

def run_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        code = f.read()
    print(f"Ejecutando archivo: {filename}\n" + "-" * 30)
    try:
        result = NodeVisitors().interpret(code)
        if result is not None:
            print("Resultado:", result)
    except Exception as e:
        print("Error de ejecución:", e)

def repl():
    interp = NodeVisitors()
    print("Intérprete simplificado de Python. Usa exit() para salir.")
    while True:
        try:
            line = input(">>> ")
            if line.strip() == "exit()":
                break
            result = interp.interpret(line)
            if result is not None:
                print(result)
        except Exception as e:
            print("Error:", e)