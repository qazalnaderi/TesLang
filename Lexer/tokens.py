
import ply.lex as lex
import re

reserved = {
    'funk': 'FUNK',
    'return': 'RETURN',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR',
    'to': 'TO',
    'begin': 'BEGIN',
    'end': 'END',
    'int': 'INT',
    'vector': 'VECTOR',
    'str': 'STR',
    'mstr': 'MSTR',
    'bool': 'BOOL',
    'null': 'NULL',
    # 'length': 'LEN',
    'as': 'AS',
    'do': 'DO',
    'print': 'PRINT',
}

tokens = (
    'ID', 'NUMBER', 'STRING', 'MSTRING',
    'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE',
    'EQEQ', 'NEQ', 'GTEQ', 'LTEQ', 'GREATER_THAN', 'LESS_THAN', 'SEMI_COLON', 'COMMA', 'LDBLBR',
    'LPAREN', 'RPAREN', 'LCURLYEBR', 'RCURLYEBR', 'LSQUAREBR', 'RSQUAREBR',
    'OR', 'AND', 'NOT', 'RETURN_ARROW', 'RETURN',    'LSQBR',  # لیست باز
    'COLON_COLON',  # دو نقطه
    'QUESTION',  # علامت سوال
    'EQUAL', 'RDBLBR',
    'QMARK', 'COLON', 'AS', 'INT', 'VECTOR', 'STR', 'MSTR', 'BOOL', 'NULL', 'TRUE', 'FALSE', 'FUNK', 'IF', 'ELSE', 'WHILE', 'DO', 'FOR', 'TO', 'BEGIN', 'END', 'LEN', 'PRINT'
)


def remove_comments(input_text):
    protected_strings = []
    string_pattern = r'"([^"\\]|\\.)*"|\'([^\'\\]|\\.)*\''

    def replace_strings(match):
        protected_strings.append(match.group(0))
        return f"__STRING_PLACEHOLDER_{len(protected_strings) - 1}__"

    text_without_strings = re.sub(string_pattern, replace_strings, input_text)

    result = list(text_without_strings)
    i = 0
    while i < len(result):
        if i + 1 < len(result) and result[i] == '<' and result[i + 1] == '/':
            comment_start = i
            i += 2
            nesting_level = 1

            while i < len(result) and nesting_level > 0:
                if i + 1 < len(result) and result[i] == '<' and result[i + 1] == '/':
                    nesting_level += 1
                    i += 2
                elif i + 1 < len(result) and result[i] == '/' and result[i + 1] == '>':
                    nesting_level -= 1
                    i += 2
                else:
                    i += 1

            if nesting_level == 0:
                for j in range(comment_start, i):
                    if result[j] != '\n':
                        result[j] = ' '
            else:
                i = comment_start + 1
        else:
            i += 1

    result = ''.join(result)

    for idx, s in enumerate(protected_strings):
        result = result.replace(f"__STRING_PLACEHOLDER_{idx}__", s)

    return result


def t_MSTRING(t):
    r'"""[\s\S]*?"""'
    t.lexer.lineno += t.value.count('\n')
    return t


def t_STRING(t):
    r'"([^\n"\\]|\\.)*"|\'([^\n\'\\]|\\.)*\''
    t.lexer.lineno += t.value.count('\n')
    return t


t_PLUS = r'\+'
t_MINUS = r'\-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'\/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LSQUAREBR = r'\['
t_RSQUAREBR = r'\]'
t_LDBLBR = r'\[\['
t_RDBLBR = r'\]\]'
t_LCURLYEBR = r'\{'
t_RCURLYEBR = r'\}'
t_SEMI_COLON = r';'
t_EQUAL = r'='
t_COLON_COLON = r'::'
t_COLON = r':'
t_QUESTION = r'\?'
t_COMMA = r','
t_RETURN_ARROW = r'=>'

t_EQEQ = r'=='
t_NEQ = r'!='
t_LTEQ = r'<='
t_GTEQ = r'>='
t_LESS_THAN = r'<'
t_GREATER_THAN = r'>'
t_AND = r'\&\&'
t_OR = r'\|\|'
t_NOT = r'!'



def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.lexer.column = 1


def t_whitespace(t):
    r'[ \t]+'
    t.lexer.column += len(t.value)
    pass


def t_error(t):
    error_patterns = {
        '@': r'@[a-zA-Z_][a-zA-Z_0-9]*',
        '#': r'#[a-zA-Z_][a-zA-Z_0-9]*',
        '$': r'\$[a-zA-Z_][a-zA-Z_0-9]*',
        '': r'.*?',
        '%': r'%',
        '~': r'~',
        '^': r'\^',
        '\\': r'\\',
        '""': r'""[^"]',
        "''": r"''[^']",
    }

    if t.value[0] in ["'", '"']:
        if t.value[0] == '"' and len(t.value) >= 3 and t.value[:3] == '"""':
            match = re.match(r'"""[^"]*', t.value)
            if match:
                illegal_token = match.group(0)
                print(f"Unclosed multi-line string '{illegal_token}' at line {t.lexer.lineno}")
                t.value = illegal_token
                t.lexer.skip(len(illegal_token))
                return None
        else:
            delimiter = t.value[0]
            match = re.match(rf'{delimiter}[^{delimiter}\\]*(?:\\.[^{delimiter}\\]*)*', t.value)
            if match:
                illegal_token = match.group(0)
                print(f"Unclosed string '{illegal_token}' at line {t.lexer.lineno}")
                t.value = illegal_token
                t.lexer.skip(len(illegal_token))
                return None

    for first_char, pattern in error_patterns.items():
        if t.value.startswith(first_char):
            match = re.match(pattern, t.value)
            if match:
                illegal_token = match.group(0)
                print(f"Illegal token '{illegal_token}' at line {t.lexer.lineno}")
                t.value = illegal_token
                t.lexer.skip(len(illegal_token))
                return None

    print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.value = t.value[0]
    t.lexer.skip(1)
    return None

def t_NUMBER(t):
    r'\d+'  # این الگو تمام اعداد صحیح را شناسایی می‌کند
    t.value = int(t.value)  # تبدیل به عدد صحیح
    return t

lexer = lex.lex()

lexer.column = 1


def find_column(input_text, token):
    last_cr = input_text.rfind('\n', 0, token.lexpos)
    if last_cr < 0:
        column = token.lexpos + 1
    else:
        column = token.lexpos - last_cr
    return column


def tokenize(input_text):
    processed_text = remove_comments(input_text)
    lexer.input(processed_text)
    lexer.lineno = 1
    lexer.column = 1
    tokens_list = []

    while True:
        tok = lexer.token()

        if not tok:
            break

        tok.column = find_column(processed_text, tok)

        lexer.column += len(str(tok.value))

        tokens_list.append(tok)
    return tokens_list