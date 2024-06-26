from ply import lex
from ply import yacc
import os
import random

class ASTNode:
    def __init__(self, type, children=None, value=None):
        self.type = type
        self.children = children if children else []
        self.value = value


class Parser:
    """
    Base class for a lexer/parser that has the rules defined as methods
    """
    tokens = ()
    precedence = ()
  
    symbol_table = {}

    def __init__(self, **kw):
        self.debug = kw.get('debug', 0)
        self.names = {}
        self.symbol_table = {}
        try:
            modname = os.path.split(os.path.splitext(__file__)[0])[
                1] + "_" + self.__class__.__name__
        except:
            modname = "parser" + "_" + self.__class__.__name__
        self.debugfile = modname + ".dbg"
        # print self.debugfile

        # Build the lexer and parser
        lex.lex(module=self, debug=self.debug)
        yacc.yacc(module=self,
                  debug=self.debug,
                  debugfile=self.debugfile)

    def run(self):
        while True:
            try:
                s = input('snailz > ')
            except EOFError:
                break
            if not s:
                continue
            parse_tree = yacc.parse(s)
            if parse_tree:
                # self.print_ast(parse_tree)
                self.eval(parse_tree)
class Snailz(Parser):
    
    tokens =  ('TRUE', 'FALSE', 'PRINT','PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LPAREN', 'RPAREN',
           'NAME', 'NUMBER', 'AND', 'OR', 'GR8R', 'LBRA', 'RBRA', 'COM',
            'COMPEQU', 'EQUALS', 'LES', 'MOD', 'SORT',
           'NOT', 'EXP','IF','WHILE','FOR','ELSE','SNAIL','STRING')

    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    #t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
    t_AND = r'\&'
    t_OR = r'\|'
    t_GR8R = r'\>'
    t_LBRA = r'\['
    t_RBRA = r'\]'
    t_COM = r'\,'
    t_COMPEQU = r'\=='
    t_EQUALS = r'\='
    t_LES = r'\<'
    t_MOD = r'\%'
    t_SORT = r'\>>'
    t_NOT = r'\!'
    t_EXP = r'\^'
    ##t_IF = r'if'
    t_WHILE  = r'while'
    t_FOR = r'for'
    t_ELSE = r'else'
    t_SNAIL = r'snail'
    t_STRING = r'"([^"\\]|\\.)*"'

    def t_PRINT(self, t):
        r'ThereneverisaslowerpaceThansnailscompetinginarace'
        return t
    
    def t_TRUE(self, t):
        r'True'
        t.value = True
        return t

    def t_FALSE(self, t):
        r'False'
        t.value = False
        return t
    def t_IF(self, t):
        r'if'
        #print("IF token detected")
        return t
    
    def t_NAME(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        if t.value in ('if', 'else', 'while', 'for','snail', 'ThereneverisaslowerpaceThansnailscompetinginarace'):  # Exclude 'if' and 'else' from being recognized as variable names
            t.type = t.value.upper()   # Convert keyword to uppercase to match token type
        return t
    

    def t_NUMBER(self, t):
        r'\d+'
        try:
            t.value = int(t.value)
        except ValueError:
            print("Integer value too large %s" % t.value)
            t.value = 0
        # print "parsed number %s" % repr(t.value)
        return t

    t_ignore = " \t"

    # t_ignore_WHITESPACE = r'\s+' # allows for both 3>2 and 3 > 2 to work but doesnt reconize token in second one

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")
    
    def bogo_sort(self, lst):
        # Bogo sort implementation (not efficient, for demonstration purposes only)
        while not self.is_sorted(lst):
            random.shuffle(lst)
        return lst
    

    def is_sorted(self, lst):
        # Check if a list is sorted
        return all(lst[i] <= lst[i+1] for i in range(len(lst)-1))

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def eval(self, node):
        if node.type == 'number':
            return node.value
        elif node.type == 'boolean':
            return node.value
        elif node.type == 'uminus':  # Handle unary negation
            operand_val = self.eval(node.children[0])
            return -operand_val  # Return the negation of the operand value
        elif node.type == 'WHILE':
            # Loop as long as the condition evaluates to True
            while self.eval(node.children[0]):
                self.eval(node.children[1])
        elif node.type == 'FOR':
            # Unpack the children of the FOR node
            while self.eval(node.children[0]):
                self.eval(node.children[1])
                self.eval(node.children[2])
        elif node.type == 'SNAIL':
            snail = 1000
            while(snail>0):
                print("SNAILZ")
                snail = snail-1
        elif node.type == 'IF':
            condition_result = self.eval(node.children[0])  # Evaluates the condition
            # print("Condition Result:", "True" if condition_result else "False")
            if condition_result:
                return self.eval(node.children[1])  # Execute if the condition is True
            elif len(node.children) > 2:
                return self.eval(node.children[2])  # Execute the else branch if it exists
            return None
        elif node.type == 'assignment':
            # Store the variable and its value in the symbol table
            variable_name = node.children[0].value
            expression_result = self.eval(node.children[1])
            self.symbol_table[variable_name] = expression_result
        elif node.type == 'string':
            variable_name = node.children[0]
            print("STRING",node.children[1])
            self.symbol_table[variable_name] = node.children[1]

        elif node.type == 'statement_expr':
            # Evaluate the expression and return the result
            return self.eval(node.children[0])
        elif node.type == 'variable':
            # Lookup variable value from symbol table
            if node.value in self.symbol_table:
                return self.symbol_table[node.value]
            else:
                raise Exception(f"Variable '{node.value}' not defined")
        elif node.type in ('+', '-', '*', '/'):
            left_val = self.eval(node.children[0])
            right_val = self.eval(node.children[1])
            if node.type == '+':
                return left_val + right_val
            elif node.type == '-':
                return left_val - right_val
            elif node.type == '*':
                return left_val * right_val
            elif node.type == '/':
                return left_val / right_val  # Handle division by zero
        elif node.type == 'exp':
            # Evaluate the exponentiation operation
            base = self.eval(node.children[0])
            exponent = self.eval(node.children[1])
            result = base ** exponent
            return result
        elif node.type == 'GR8R':
            left_val = self.eval(node.children[0])
            right_val = self.eval(node.children[1])
            return left_val > right_val
        elif node.type == 'LES':
            left_val = self.eval(node.children[0])
            right_val = self.eval(node.children[1])
            return left_val < right_val
        elif node.type == 'COMPEQU':
            left_val = self.eval(node.children[0])
            right_val = self.eval(node.children[1])
            return left_val == right_val
        elif node.type == 'NOT':
            operand_val = self.eval(node.children[0])
            return not operand_val
        elif node.type == 'AND':
            left_val = self.eval(node.children[0])
            right_val = self.eval(node.children[1])
            return left_val and right_val
        elif node.type == 'OR':
            left_val = self.eval(node.children[0])
            right_val = self.eval(node.children[1])
            return left_val or right_val
        elif node.type == 'list':
            # Evaluate each expression within the comma-separated list
            return [self.eval(child) for child in node.children]
        # Add logic for other expression types (comparison, negation, etc.)
        elif node.type == 'sort':
            # Assume the child node is a variable containing the list
            list_var_name = node.children[0].value
            if list_var_name in self.symbol_table:
                unsorted_list = self.symbol_table[list_var_name]
                sorted_list = self.bogo_sort(unsorted_list)
                return sorted_list
        elif node.type == 'print':
            # Evaluate the expression inside the print statement
            print_value = self.eval(node.children[0])
            print(print_value)  # Print the result
            return None 
        else:
            raise Exception(f"Unknown node type: {node.type}")
    
    precedence = (
    ('nonassoc', 'GR8R', 'LES', 'COMPEQU'),
    ('left', 'AND', 'OR'),
    ('right', 'NOT'),
    ('left', 'PLUS', 'MINUS'),
    ('right', 'EXP'),  # Exponentiation
    ('left', 'TIMES', 'DIVIDE'),
    ('left', 'MOD'),
    ('right', 'UMINUS'),
    ('right', 'IF', 'ELSE', 'WHILE', 'FOR'),  # Include WHILE here if necessary
    ('nonassoc', 'LBRA', 'RBRA'),
    )

    def p_statement_assign(self, p):
        'statement : NAME EQUALS expression'
        # Store the variable and its value in the symbol table
        # a ###### self.symbol_table[p[1]] = self.eval(p[3])
        p[0] = ASTNode('assignment', [ASTNode('variable', value=p[1]), p[3]])
    
    def p_string(self,p):
        'statement : NAME EQUALS STRING'
        p[0] = ASTNode('string', children=[p[1],p[3]])

    def p_statement_expr(self, p):
        '''statement : expression'''
        # Evaluate the expression and store the value
        result = self.eval(p[1])
        p[0] = ASTNode('statement_expr', children=[p[1]], value=result)

    def p_expression_binop(self, p):
        """
        expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
        """
        p[0] = ASTNode(p[2], [p[1], p[3]])

    def p_expression_uminus(self, p):
        'expression : MINUS expression %prec UMINUS'
        p[0] = ASTNode('uminus', [p[2]])

    def p_expression_group(self, p):
        'expression : LPAREN expression RPAREN'
        p[0] = p[2]

    def p_expression_number(self, p):
        'expression : NUMBER'
        p[0] = ASTNode('number', value=p[1])

    def p_expression_name(self, p):
        'expression : NAME'
        p[0] = ASTNode('variable', value=p[1])

    def p_expression_exp(self, p):
        """
        expression : expression EXP expression
        """
        p[0] = ASTNode('exp', [p[1], p[3]])

    def p_expression_mod(self, p):
        """
        expression : expression MOD expression
        """
        p[0] = ASTNode('mod', [p[1], p[3]])

    def p_expression_gr8r(self, p):
        """
        expression : expression GR8R expression
        """
        p[0] = ASTNode('GR8R', [p[1], p[3]])

    def p_expression_les(self, p):
        """
        expression : expression LES expression
        """
        p[0] = ASTNode('LES', [p[1], p[3]])

    def p_expression_compequ(self, p):
        """
        expression : expression COMPEQU expression
        """
        p[0] = ASTNode('COMPEQU', [p[1], p[3]])

    def p_expression_lbra(self, p):
        """
        expression : LBRA expression RBRA
        """
        p[0] = p[2]

    def p_expression_rbra(self, p):
        """
        expression : RBRA expression RBRA
        """
        p[0] = p[2]

    def p_expression_list(self, p):
        """
        expression : LBRA list_elements RBRA
        """
        p[0] = ASTNode('list', children=p[2])
    
    def p_list_elements(self, p):
        """
        list_elements : expression
                      | list_elements COM expression
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_expression_sort(self, p):
        'expression : SORT LPAREN expression RPAREN'
        # Here, we create a sort node with the inner expression as a child
        p[0] = ASTNode('sort', [p[3]])


    def p_expression_and(self, p):
        """
        expression : expression AND expression
        """
        p[0] = ASTNode('AND', [p[1], p[3]])

    def p_expression_or(self, p):
        """
        expression : expression OR expression
        """
        p[0] = ASTNode('OR', [p[1], p[3]])

    def p_expression_not(self, p):
        """
        expression : NOT expression
        """
        p[0] = ASTNode('NOT', [p[2]])

     # Grammar rules
    def p_statement_if(self, p):
        """
        statement : IF expression statement
                | IF expression statement ELSE statement
        """
        if len(p) == 4:
            # No else branch
            p[0] = ASTNode('IF', children=[p[2], p[3]])
        else:
            # Includes else branch
            p[0] = ASTNode('IF', children=[p[2], p[3], p[5]])
            
    def p_statement_while(self, p):
        """
        statement : WHILE LPAREN expression RPAREN statement
        """
        p[0] = ASTNode('WHILE', children=[p[3], p[5]])
    
    def p_statement_snail(self,p):
        """
        statement : SNAIL
        """
        p[0] = ASTNode('SNAIL')

    def p_statement_for(self, p):
        """
        statement : FOR LPAREN expression statement RPAREN statement
        """
        p[0] = ASTNode('FOR', children=[p[3], p[4], p[6]])

    def p_statement_print(self, p):
        'statement : PRINT LPAREN expression RPAREN'
        p[0] = ASTNode('print', children=[p[3]])
    
    def p_expression_boolean(self, p):
        '''expression : TRUE
                    | FALSE'''
        p[0] = ASTNode('boolean', value=p[1])


    def p_error(self, p):
        if p:
            print("Syntax error at '%s'" % p.value)
        else:
            print("Syntax error at EOF")

    # Method to print the AST
    # def print_ast(self, node, indent=0):
        # print(' ' * indent + node.type)
        # if node.value is not None:
           # print(' ' * (indent + 2) + str(node.value))
       # for child in node.children:
            # self.print_ast(child, indent + 2)


if __name__ == '__main__':
    snailz = Snailz()
    snailz.run()

    # After parsing, print the AST
    ast_root = snailz.parse_result
    snailz.print_ast(ast_root)

