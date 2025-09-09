# InterpretePython

**InterpretePython** es un proyecto desarrollado en Python que implementa un intérprete para el lenguaje Python. Este repositorio está diseñado para ayudar a comprender cómo funciona un intérprete de Python desde cero y puede servir como base educativa o para proyectos de análisis y ejecución de código Python de manera personalizada.

## Características principales

- **Parseo y análisis léxico**: Convierte el código fuente en tokens que pueden ser procesados por el intérprete.
- **Evaluación de expresiones**: Soporta operaciones aritméticas, asignaciones, y el manejo de variables.
- **Ejecución de instrucciones**: Permite ejecutar sentencias simples y compuestas, como condicionales (`if`, `else`), bucles (`while`, `for`), y funciones definidas por el usuario.
- **Gestión de errores**: Informa sobre errores de sintaxis y ejecución para facilitar el debug del código interpretado.
- **Extensibilidad**: El diseño modular permite agregar nuevas funcionalidades y ampliar el lenguaje interpretado.

## ¿Cómo funciona?

El intérprete toma un archivo de texto (`.py`) o una cadena con código Python, lo analiza y ejecuta línea por línea, simulando el comportamiento de Python. Provee un entorno seguro y controlado para experimentar con código Python, ideal para propósitos educativos y pruebas.

### Flujo básico

1. **Entrada de código**: El usuario proporciona el código a interpretar.
2. **Tokenización**: El código se divide en tokens reconocibles.
3. **Parseo**: Los tokens se estructuran en un árbol de sintaxis abstracta (AST).
4. **Ejecución**: El AST se recorre y se ejecutan las instrucciones correspondientes.

## Instalación

Clona el repositorio y asegúrate de tener Python instalado (versión 3.7 o superior):

```bash
git clone https://github.com/Jorgito091/InterpretePython.git
cd InterpretePython
```

Puedes instalar las dependencias (si las hay) usando:

```bash
pip install -r requirements.txt
```

> **Nota:** Si no existe el archivo `requirements.txt`, significa que no se requieren módulos externos.

## Uso

Ejecuta el intérprete pasando un archivo Python como argumento:

```bash
python interprete.py ejemplo.py
```

O accede al modo interactivo:

```bash
python interprete.py
```

## Ejemplos de uso

### Ejemplo 1: Asignación y operaciones

```python
x = 10
y = 5
resultado = x + y * 2
print(resultado)  # Salida esperada: 20
```

### Ejemplo 2: Estructuras de control

```python
n = 3
if n > 0:
    print("Número positivo")
else:
    print("Número negativo o cero")
```

### Ejemplo 3: Bucles

```python
for i in range(5):
    print(i)
```

### Ejemplo 4: Funciones

```python
def suma(a, b):
    return a + b

print(suma(3, 7))  # Salida esperada: 10
```

## Contribución

Si deseas colaborar, puedes hacer un fork del proyecto, crear una rama con tus cambios y enviar un pull request. Todas las sugerencias y mejoras son bienvenidas.

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---

**Autor:** [Jorgito091](https://github.com/Jorgito091)

¿Tienes dudas o sugerencias? ¡Abre un issue!