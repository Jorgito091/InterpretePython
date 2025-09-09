# InterpretePython

**InterpretePython** es un proyecto desarrollado en Python que implementa un intérprete para el lenguaje Python. Este repositorio está diseñado para ayudar a comprender cómo funciona un intérprete de Python desde cero y puede servir como base educativa o para proyectos de análisis y ejecución de código Python de manera personalizada.

## Características principales

- **Parseo y análisis léxico**: Convierte el código fuente en tokens que pueden ser procesados por el intérprete.
- **Evaluación de expresiones**: Soporta operaciones aritméticas, asignaciones y el manejo de variables.
- **Ejecución de instrucciones**: Permite ejecutar sentencias simples y compuestas, como condicionales (`if`, `else`), bucles (`while`, `for`) y funciones definidas por el usuario.
- **Gestión de errores**: Informa sobre errores de sintaxis y ejecución para facilitar el debug del código interpretado.
- **Extensibilidad**: El diseño modular permite agregar nuevas funcionalidades y ampliar el lenguaje interpretado.

## ¿Cómo funciona el intérprete?

El intérprete está compuesto por varias etapas y módulos principales que juntos permiten analizar y ejecutar código Python. A continuación se explica su lógica interna:

### 1. **Tokenización (Análisis léxico)**
El código fuente se convierte en una secuencia de *tokens*, que son las unidades mínimas significativas (palabras clave, operadores, literales, etc.). Este proceso permite separar y identificar cada elemento del código para su posterior análisis.

### 2. **Parseo (Análisis sintáctico)**
Los tokens generados se agrupan siguiendo las reglas del lenguaje Python y se estructuran en un Árbol de Sintaxis Abstracta (AST). El AST representa la jerarquía de las operaciones y sentencias, facilitando su interpretación.

### 3. **Evaluación y ejecución**
El intérprete recorre el AST y evalúa cada nodo según su tipo:
- **Expresiones**: Calcula valores o resultados.
- **Asignaciones**: Guarda valores en variables.
- **Sentencias de control**: Ejecuta bloques de código según condiciones (`if`, `while`, `for`).
- **Funciones**: Permite definir y llamar funciones, gestionando el alcance de variables.
- **Impresión y salida**: Muestra resultados en pantalla.

El entorno de ejecución mantiene el estado de todas las variables y funciones, simulando el comportamiento de Python real.

### 4. **Gestión de errores**
El intérprete detecta errores de sintaxis (estructura incorrecta) y de ejecución (por ejemplo, dividir por cero o acceder a una variable no definida). Informa al usuario con mensajes descriptivos para facilitar la corrección.

## Instalación

No requiere módulos externos. Simplemente clona el repositorio y asegúrate de tener Python instalado (versión 3.7 o superior):

```bash
git clone https://github.com/Jorgito091/InterpretePython.git
cd InterpretePython
```

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
