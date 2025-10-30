global_var = "soy global"

def nivel_global():
    x = "nivel_global"

    def nivel_intermedio(a, b=2, factor=1):
        y = "nivel_intermedio"

        def nivel_interno(z):
            nonlocal y
            y = "modificado_en_interno"
            total = (a + b + z) * factor
            print("[nivel_interno] total:", total)
            print("[nivel_interno] closure vars ->", x, y, global_var)
            return total

        tupla = (1, 2, 3)
        a1 = tupla[0]
        lista = [4, 5, 6]
        lista[1:3] = [7, 8]
        print("[nivel_intermedio] a1:", a1)
        print("[nivel_intermedio] lista modificada:", lista)

        class Objeto: pass
        obj = Objeto()
        setattr(obj, "dato", 42)
        print("[nivel_intermedio] getattr(obj, 'dato') =", getattr(obj, "dato"))

        datos = list(range(10))
        print("[nivel_intermedio] datos[2:8:2] =", datos[2:8:2])

        return nivel_interno(3)

    return nivel_intermedio

f = nivel_global()
print("\n=== Prueba de parámetros ===")
resultado = f(5, 2, 2)  # <-- factor pasado como posicional
print("Resultado final:", resultado)