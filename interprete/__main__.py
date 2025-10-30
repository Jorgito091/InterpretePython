# __main__.py
from .runner import run_file
import os

def main():
    # Asume que proof.py está en la misma carpeta que __main__.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(current_dir, "proof.py")

    if not os.path.isfile(filename):
        print(f"No se encontró el archivo {filename}")
        return

    run_file(filename)

if __name__ == "__main__":
    main()