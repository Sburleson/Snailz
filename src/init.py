from ply import lex, yacc

# Define tokens
tokens = (
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LPAREN', 'RPAREN',
    'NAME', 'NUMBER', 'AND', 'OR', 'GR8R', 'LBRA', 'RBRA', 'EQUAL',
    'COM', 'QUOTE', 'PERIOD', 'SCOLN', 'COMPEQU', 'LES', 'MOD', 'SORT', 
    'COMMENT', 'NOT', 'VAR', 'SHELL', 'SLOW', 'SLIME', 'SPIRAL', 'SNAIL', 'ESCARGO',
    'IF', 'ELSE', 'WHILE', 'FOR', 'RETURN', 'SLEEP', 'TRY', 'CATCH'
)

# Regular expression rules for tokens
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
t_AND = r'\&'
t_OR = r'\|'
t_GR8R = r'\>'
t_LBRA = r'\['
t_RBRA = r'\]'
t_COM = r'\,'
t_QUOTE = r'\"|\''
t_PERIOD = r'\.'
t_SCOLN = r'\;'
t_COMPEQU = r'\=='
t_LES = r'\<'
t_MOD = r'\%'
t_SORT = r'\>>'
t_NOT = r'\!'
t_NUMBER = r'\d+'
t_EQUAL = r'='
t_SHELL = r'SHELL'
t_SLOW = r'SLOW'
t_SLIME = r'SLIME'
t_SPIRAL = r'SPIRAL'
t_SNAIL = r'SNAIL'
t_ESCARGO = r'ESCARGO'
t_IF = r'IF'
t_ELSE = r'ELSE'
t_WHILE = r'WHILE'
t_FOR = r'FOR'
t_RETURN = r'RETURN'
t_SLEEP = r'SLEEP'
t_TRY = r'TRY'
t_CATCH = r'CATCH'

# Ignored characters
t_ignore = ' \t'

# Define a rule to track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Error handling rule
def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

# Build lexer
lexer = lex.lex()

# Parsing rules
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)

# Dictionary for symbol table
symbol_table = {}

# Parsing rules
def p_statement_expression(p):
    '''statement : expression
                 | assignment
                 | var_declaration
                 | if_statement
                 | while_loop
                 | for_loop
                 | return_statement
                 | sleep_statement
                 | try_catch_statement'''
    p[0] = p[1]

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression COMPEQU expression'''
    p[0] = ('binop', p[2], p[1], p[3])

def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = ('number', p[1])

def p_expression_name(p):
    'expression : NAME'
    p[0] = ('name', p[1])

def p_assignment(p):
    'assignment : VAR NAME EQUAL expression'
    symbol_table[p[2]] = p[4]
    p[0] = ('assignment', p[2], p[4])

def p_var_declaration(p):
    '''var_declaration : VAR NAME EQUAL expression
                       | VAR NAME'''
    if len(p) == 5:
        symbol_table[p[2]] = p[4]
    p[0] = ('var_declaration', p[2], p[4] if len(p) == 5 else None)

def p_if_statement(p):
    '''if_statement : IF LPAREN expression RPAREN statement
                    | IF LPAREN expression RPAREN statement ELSE statement'''
    if len(p) == 6:
        p[0] = ('if_statement', p[3], p[5], None)
    else:
        p[0] = ('if_statement', p[3], p[5], p[7])

def p_while_loop(p):
    'while_loop : WHILE LPAREN expression RPAREN statement'
    p[0] = ('while_loop', p[3], p[5])

def p_for_loop(p):
    'for_loop : FOR LPAREN expression SCOLN expression SCOLN expression RPAREN statement'
    p[0] = ('for_loop', p[3], p[5], p[7], p[9])

def p_return_statement(p):
    'return_statement : RETURN expression'
    p[0] = ('return_statement', p[2])

def p_sleep_statement(p):
    'sleep_statement : SLEEP expression'
    p[0] = ('sleep_statement', p[2])

def p_try_catch_statement(p):
    'try_catch_statement : TRY statement catch_blocks'
    p[0] = ('try_catch_statement', p[2], p[3])

def p_catch_blocks(p):
    '''catch_blocks : catch_block
                    | catch_block catch_blocks'''
    p[0] = [p[1]] if len(p) == 2 else [p[1]] + p[2]

def p_catch_block(p):
    'catch_block : CATCH LPAREN NAME RPAREN statement'
    p[0] = ('catch_block', p[3], p[5])

def p_error(p):
    print(f"Syntax error at '{p.value}'")

# Build parser
parser = yacc.yacc()

# Test the parser
data = '''
VAR x = 10;
IF (x > 5) SLEEP 10;
'''

parsed_data = parser