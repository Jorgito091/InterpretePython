import re
import sys

# --- Definición de Tokens ---
TOKEN_SPEC = [
    ("NUMBER",      r'\d+(\.\d+)?'),       # Números enteros y flotantes
    ("STRING",      r'\".*?\"|\'.*?\''),   # Cadenas entre comillas
    ("ID",          r'[a-zA-Z_][a-zA-Z0-9_]*'),  # Identificadores
    ("ASSIGN",      r'='),                 # =
    ("OP",          r'[+\-*/%]'),          # Operadores
    ("COMPARE",     r'==|!=|<=|>=|<|>'),   # Comparaciones
    ("LPAREN",      r'\('),                # (
    ("RPAREN",      r'\)'),                # )
    ("LBRACE",      r'\{'),                # {
    ("RBRACE",      r'\}'),                # }
    ("LBRACKET",    r'\['),                # [
    ("RBRACKET",    r'\]'),                # ]
    ("COMMA",       r','),                 # ,
    ("COLON",       r':'),                 # :
    ("NEWLINE",     r'\n'),                # Saltos de línea
    ("SKIP",        r'[ \t]+'),            # Espacios y tabs
    ("COMMENT",     r'\#.*'),              # Comentarios
]

# Palabras reservadas del lenguaje
KEYWORDS = {
    "if", "else", "for", "while", "def", "return",
    "class", "in", "and", "or", "not", "True", "False", "None"
}

token_regex = "|".join(f"(?P<{name}>{regex})" for name, regex in TOKEN_SPEC)

def lexer(code):
    tokens = []
    for match in re.finditer(token_regex, code):
        kind = match.lastgroup
        lexeme = match.group()

        if kind == "ID" and lexeme in KEYWORDS:
            kind = "KEYWORD"
        elif kind == "SKIP" or kind == "COMMENT":
            continue

        tokens.append((lexeme, kind))
    return tokens

# --- Ejecución desde terminal ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 IL.py <archivo_a_analizar.py>")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        with open(filename, "r", encoding="utf-8") as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: archivo '{filename}' no encontrado.")
        sys.exit(1)

    result = lexer(code)
    for lexema, token in result:
        print(f"{lexema:15} --> {token}")