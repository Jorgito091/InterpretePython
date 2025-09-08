import re
import operator

# =============================
# Lexer
# =============================

def tokenize(code):
    # Remove comments
    code = re.sub(r'#.*', '', code)
    # Token regex
    token_spec = r'\".*?\"|\'.*?\'|\bdef\b|\bif\b|\belse\b|\bwhile\b|True|False|and|or|not|[A-Za-z_]\w*|\d+\.\d+|\d+|==|!=|<=|>=|[+\-*/%=<>(){},:]'
    tokens = re.findall(token_spec, code)
    return [tok for tok in tokens if tok.strip() != '']

# =============================
# Parser (Shunting Yard for expr)
# =============================

precedence = {
    'or': 1,
    'and': 2,
    'not': 3,
    '==': 4, '!=': 4, '>': 4, '<': 4,
    '+': 5, '-': 5,
    '*': 6, '/': 6, '%': 6,
}

right_assoc = {'not'}

def shunting_yard(tokens):
    output = []
    stack = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if re.match(r'\d+\.\d+|\d+', tok) or re.match(r'\".*\"|\'.*\'', tok) or tok in ['True', 'False'] or re.match(r'[A-Za-z_]\w*', tok):
            output.append(tok)
        elif tok in precedence:
            while stack and stack[-1] in precedence and (
                (tok not in right_assoc and precedence[tok] <= precedence[stack[-1]]) or
                (tok in right_assoc and precedence[tok] < precedence[stack[-1]])
            ):
                output.append(stack.pop())
            stack.append(tok)
        elif tok == '(':
            stack.append(tok)
        elif tok == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        else:
            output.append(tok)
        i += 1
    while stack:
        output.append(stack.pop())
    return output

def parse_primary(token):
    if re.match(r'^\d+\.\d+$', token):
        return float(token)
    elif re.match(r'^\d+$', token):
        return int(token)
    elif token in ('True', 'False'):
        return token == 'True'
    elif re.match(r'^\".*\"|\'.*\'$', token):
        return token[1:-1]
    else:
        return token

def build_ast(rpn):
    stack = []
    ops = {
        '+': operator.add, '-': operator.sub,
        '*': operator.mul, '/': operator.truediv, '%': operator.mod,
        '==': operator.eq, '!=': operator.ne, '>': operator.gt, '<': operator.lt,
        'and': lambda x, y: x and y, 'or': lambda x, y: x or y,
        'not': lambda x: not x
    }
    for tok in rpn:
        if tok in ops:
            if tok == 'not':
                val = stack.pop()
                stack.append(('not', val))
            else:
                right = stack.pop()
                left = stack.pop()
                stack.append((tok, left, right))
        else:
            stack.append(parse_primary(tok))
    return stack[0] if stack else None

# =============================
# Statement Parser (if/while/def)
# =============================

def parse_block(lines, start):
    block = []
    indent = None
    for i in range(start, len(lines)):
        if not lines[i].strip():
            continue
        curr_indent = len(lines[i]) - len(lines[i].lstrip())
        if indent is None:
            indent = curr_indent
        elif curr_indent < indent:
            break
        block.append(lines[i][indent:])
    return block, i

def parse_statements(lines):
    i = 0
    stmts = []
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith('#'):
            i += 1
            continue
        if line.startswith('def '):
            m = re.match(r'def\s+([A-Za-z_]\w*)\((.*?)\):', line)
            name = m.group(1)
            params = [p.strip() for p in m.group(2).split(',') if p.strip()]
            block, next_i = parse_block(lines, i+1)
            stmts.append(('def', name, params, block))
            i = next_i
            continue
        elif line.startswith('if '):
            cond = line[3:line.index(':')].strip()
            block, next_i = parse_block(lines, i+1)
            stmts.append(('if', cond, block))
            i = next_i
            continue
        elif line.startswith('while '):
            cond = line[6:line.index(':')].strip()
            block, next_i = parse_block(lines, i+1)
            stmts.append(('while', cond, block))
            i = next_i
            continue
        elif line.startswith('else:'):
            block, next_i = parse_block(lines, i+1)
            stmts.append(('else', block))
            i = next_i
            continue
        else:
            stmts.append(('expr', line))
        i += 1
    return stmts

# =============================
# Environment / Funciones
# =============================

class Environment(dict):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
    def get(self, key):
        return self[key] if key in self else (self.parent.get(key) if self.parent else None)
    def set(self, key, value):
        self[key] = value

functions = {}

def eval_expr_ast(ast, env):
    if isinstance(ast, tuple):
        op = ast[0]
        if op == 'not':
            return not eval_expr_ast(ast[1], env)
        left = eval_expr_ast(ast[1], env)
        right = eval_expr_ast(ast[2], env)
        if op == '/' and right == 0:
            raise ZeroDivisionError("División por cero")
        ops = {
            '+': operator.add, '-': operator.sub, '*': operator.mul,
            '/': operator.truediv, '%': operator.mod,
            '==': operator.eq, '!=': operator.ne, '>': operator.gt, '<': operator.lt,
            'and': lambda x, y: x and y, 'or': lambda x, y: x or y
        }
        return ops[op](left, right)
    elif isinstance(ast, str):
        val = env.get(ast)
        if val is None:
            raise NameError(f"Variable '{ast}' no definida")
        return val
    else:
        return ast

def evaluate(stmt, env):
    if stmt[0] == 'expr':
        line = stmt[1]
        if '=' in line:
            var, expr = line.split('=', 1)
            var = var.strip()
            expr = expr.strip()
            toks = tokenize(expr)
            rpn = shunting_yard(toks)
            ast = build_ast(rpn)
            val = eval_expr_ast(ast, env)
            env.set(var, val)
            return None
        elif re.match(r'[A-Za-z_]\w*\(.*\)', line):
            m = re.match(r'([A-Za-z_]\w*)\((.*?)\)', line)
            fname = m.group(1)
            args = [a.strip() for a in m.group(2).split(',') if a.strip()]
            if fname == 'print':
                vals = []
                for arg in args:
                    toks = tokenize(arg)
                    rpn = shunting_yard(toks)
                    ast = build_ast(rpn)
                    vals.append(eval_expr_ast(ast, env))
                print(*vals)
                return None
            elif fname == 'input':
                prompt = args[0] if args else ''
                return input(prompt)
            elif fname in functions:
                fdef = functions[fname]
                local_env = Environment(env)
                for p, v in zip(fdef['params'], args):
                    toks = tokenize(v)
                    rpn = shunting_yard(toks)
                    ast = build_ast(rpn)
                    local_env.set(p, eval_expr_ast(ast, env))
                for s in fdef['body']:
                    res = evaluate(s, local_env)
                    if res is not None:
                        return res
            else:
                raise NameError(f"Función '{fname}' no definida")
        else:
            toks = tokenize(line)
            rpn = shunting_yard(toks)
            ast = build_ast(rpn)
            val = eval_expr_ast(ast, env)
            return val
    elif stmt[0] == 'def':
        _, name, params, block = stmt
        fbody = parse_statements(block)
        functions[name] = {'params': params, 'body': fbody}
        return None
    elif stmt[0] == 'if':
        _, cond, block = stmt
        toks = tokenize(cond)
        rpn = shunting_yard(toks)
        ast = build_ast(rpn)
        if eval_expr_ast(ast, env):
            body = parse_statements(block)
            for s in body:
                evaluate(s, env)
        return None
    elif stmt[0] == 'else':
        _, block = stmt
        body = parse_statements(block)
        for s in body:
            evaluate(s, env)
        return None
    elif stmt[0] == 'while':
        _, cond, block = stmt
        while True:
            toks = tokenize(cond)
            rpn = shunting_yard(toks)
            ast = build_ast(rpn)
            if eval_expr_ast(ast, env):
                body = parse_statements(block)
                for s in body:
                    evaluate(s, env)
            else:
                break
        return None

def handle_error(e):
    if isinstance(e, SyntaxError):
        print(f"SyntaxError: {e}")
    elif isinstance(e, NameError):
        print(f"NameError: {e}")
    elif isinstance(e, ZeroDivisionError):
        print(f"ZeroDivisionError: {e}")
    else:
        print(f"Error: {e}")

# =============================
# REPL
# =============================

def main():
    print("Mini intérprete tipo Python avanzado. Escribe código, Ctrl+C para salir.")
    env = Environment()
    buffer = []
    while True:
        try:
            line = input(">>> " if not buffer else "... ")
            if line.strip() == "":
                if buffer:
                    stmts = parse_statements(buffer)
                    for stmt in stmts:
                        try:
                            res = evaluate(stmt, env)
                            if res is not None:
                                print(res)
                        except Exception as e:
                            handle_error(e)
                    buffer = []
                continue
            buffer.append(line)
        except KeyboardInterrupt:
            print("\nSaliendo.")
            break
        except Exception as e:
            handle_error(e)
            buffer = []

if __name__ == "__main__":
    main()