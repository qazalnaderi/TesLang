
from Lexer.tokens import tokens
from .ast import *
from Lexer.tokens import lexer

class Grammar:
    tokens = tokens

    # Precedence to resolve shift/reduce conflicts
    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'EQEQ', 'NEQ'),
        ('left', 'GREATER_THAN', 'LESS_THAN', 'GTEQ', 'LTEQ'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MULTIPLY', 'DIVIDE'),
        ('right', 'NOT'),
        ('right', 'QMARK', 'COLON'),
        ('nonassoc', 'IFX'),
        ('nonassoc', 'ELSE'),
    )

    def __init__(self):
        self.lexer = lexer
        self.paren_count = 0
        self.brace_count = 0
        self.current_function = None 
        self.has_syntax_error = False
        



    # prog :=
    def p_prog(self, p):
        '''prog : func_list'''
        p[0] = ProgramNode(function=p[1], prog=None, lineno=self.lexer.lineno)
        return p[0]
    def p_empty(self, p):
        'empty :'
        p[0] = None


    def p_func_list(self, p):
        '''func_list : funk
                     | funk func_list
                     | '''
        if len(p) == 1:
            p[0] = []
        elif len(p) == 2:
            p[0] = [p[1]] if p[1] else []
        else:
            p[0] = [p[1]] + p[2]

    # func :=
    def p_func_with_body(self, p):
        '''funk : FUNK ID LPAREN flist RPAREN LESS_THAN type GREATER_THAN LBRACE body RBRACE'''
        self.brace_count += 1
        self.current_function = p[2]
        param_list = []
        current = p[4]
        while current and hasattr(current, 'iden') and current.iden:
            param_list.append((current.iden, current.type.type_value))
            current = current.next_param if hasattr(current, 'next_param') else None
        p[0] = FunctionNode(type=p[7], iden=p[2], flist=p[4], func_choice=p[10], lineno=self.lexer.lineno)
        self.current_function = None
        self.brace_count -= 1

    def p_func_without_body(self, p):
        '''funk : FUNK ID LPAREN flist RPAREN LESS_THAN type GREATER_THAN RETURN_ARROW expr SEMI_COLON'''
        self.current_function = p[2]
        param_list = []
        current = p[4]
        while current and hasattr(current, 'iden'):
            param_list.append((current.iden, current.type.type_value))
            current = current.next_param if hasattr(current, 'next_param') else None
        self.defined_functions[p[2]] = {'return_type': p[7].type_value, 'params': param_list}
        p[0] = FunctionWithReturnNode(type=p[7], iden=p[2], flist=p[4], return_expr=p[10], lineno=self.lexer.lineno)
        self.current_function = None
        return p[0]

    def p_func_error(self, p):
        '''funk : error'''
        if self.brace_count > 0:
            print(f"Error: Unmatched curly brace(s) at line {self.lexer.lineno}.")
        return None

    # body :=
    def p_body(self, p):
        '''body : stmt_list'''
        p[0] = BodyNode(body=p[1], lineno=self.lexer.lineno)
        return p[0]

    def p_stmt_list(self, p):
        '''stmt_list : stmt
                     | stmt stmt_list
                     | '''
        if len(p) == 2:
            p[0] = [p[1]] if p[1] else []
        elif len(p) == 3:
            p[0] = [p[1]] + p[2] if p[1] else p[2]
        else:
            p[0] = []
        return p[0]

    # stmt :=
    def p_stmt_expr(self, p):
        '''stmt : expr SEMI_COLON'''
        p[0] = ExpressionStatementNode(expr=p[1], lineno=self.lexer.lineno)
        return p[0]

    def p_stmt_assign(self, p):
        '''stmt : expr EQUAL expr SEMI_COLON'''
        p[0] = AssignmentNode(left=p[1], right=p[3], lineno=self.lexer.lineno)
        return p[0]
    

    def p_stmt_defvar(self, p):
        '''stmt : defvar SEMI_COLON'''
        p[0] =p[1]
        return p[0]

    def p_defvar(self, p):
        '''defvar : ID COLON_COLON type
                | ID COLON_COLON type EQUAL expr'''
        
        if len(p) == 4:
            p[0] = VariableDefinitionNode(iden=p[1], type=p[3], defvar_choice=None, lineno=self.lexer.lineno)
        else:
            p[0] = VariableDefinitionNode(iden=p[1], type=p[3], defvar_choice=p[5], lineno=self.lexer.lineno)
        return p[0]


    def p_stmt_print(self, p):
        '''stmt : PRINT expr SEMI_COLON'''
        p[0] = PrintStatementNode(expr=p[2], lineno=self.lexer.lineno)
        return p[0]

    def p_stmt_if(self, p):
        '''stmt : IF LDBLBR expr RDBLBR stmt %prec IFX'''
        self.paren_count += 1
        p[0] = IfStatementNode(expr=p[3], stmt=p[5],else_choice=None, lineno=self.lexer.lineno)
        self.paren_count -= 1
        return p[0]

    def p_stmt_if_else(self, p):
        '''stmt : IF LPAREN expr RPAREN stmt ELSE stmt'''
        self.paren_count += 1
        p[0] = IfStatementNode(expr=p[3], stmt=p[5], else_stmt=p[7], lineno=self.lexer.lineno)
        self.paren_count -= 1
        return p[0]

    def p_stmt_while(self, p):
        '''stmt : WHILE LPAREN expr RPAREN stmt'''
        self.paren_count += 1
        p[0] = WhileStatementNode(condition=p[3], stmt=p[5], lineno=self.lexer.lineno)
        self.paren_count -= 1
        return p[0]

    def p_stmt_do_while(self, p):
        '''stmt : DO stmt WHILE LPAREN expr RPAREN SEMI_COLON'''
        self.paren_count += 1
        p[0] = DoWhileStatementNode(stmt=p[2], condition=p[5], lineno=self.lexer.lineno)
        self.paren_count -= 1
        return p[0]

    def p_stmt_for(self, p):
        '''stmt : FOR LPAREN ID EQUAL expr TO expr RPAREN stmt'''
        p[0] = ForStatementNode(iden=p[3], expr1=p[5], expr2=p[7], stmt=p[9], lineno=self.lexer.lineno)
        return p[0]

    def p_stmt_begin_end(self, p):
        '''stmt : BEGIN body END'''
        p[0] = BodyNode(body=p[2], lineno=self.lexer.lineno)
        return p[0]

    def p_stmt_return(self, p):
        '''stmt : RETURN expr SEMI_COLON
        | RETURN SEMI_COLON'''
        if len(p) == 4:
            p[0] = ReturnStatementNode(expr=p[2], lineno=self.lexer.lineno)
        else:
            p[0] = ReturnStatementNode(expr=None, lineno=self.lexer.lineno)


    # flist :=
    def p_flist(self, p):
        '''flist : empty
                 | ID AS type
                 | ID AS type COMMA flist'''
        if len(p) == 1:           # Empty rule
            p[0] = None
        if len(p) == 4:
            p[0] = FlistNode(iden=p[1], type=p[3], next_param=None, lineno=self.lexer.lineno)
    
        elif len(p) == 6:
            p[0] = FlistNode(iden=p[1], type=p[3], next_param=p[5], lineno=self.lexer.lineno)
        
        else:
            p[0] = None
        
        return p[0]

    # clist :=
    def p_clist(self, p):
        '''clist : empty
                 | expr
                 | expr COMMA clist'''
        if len(p) == 1:           # Empty rule
            p[0] = ClistNode(expr=[], lineno=self.lexer.lineno)
        elif len(p) == 2:
            if p[1] is None:
                p[0] = ClistNode(expr=[], lineno=self.lexer.lineno)
            else:
                p[0] = ClistNode(expr=[p[1]], lineno=self.lexer.lineno)
        else:
            p[0] = ClistNode(expr=[p[1]] + p[3].expr, lineno=self.lexer.lineno)
        return p[0]

    # type :=
    def p_type(self, p):
        '''type : INT
                | VECTOR
                | STR
                | MSTR
                | BOOL
                | NULL'''
        p[0] = TypeNode(type_value=p[1], lineno=self.lexer.lineno)
        return p[0]

    # expr :=
    def p_expr_array_indexing(self, p):
        '''expr : expr LSQUAREBR expr RSQUAREBR'''
        p[0] = ArrayIndexingNode(array_expr=p[1], index_expr=p[3], lineno=self.lexer.lineno)
        p[0].type = 'INT'  # Assuming array elements are integers
        return p[0]

    def p_expr_clist(self, p):
        '''expr : LSQUAREBR clist RSQUAREBR'''
        p[0] = ClistNode(exprs=p[2].exprs, lineno=self.lexer.lineno)
        p[0].type = 'VECTOR'
        return p[0]

    def p_expr_ternary(self, p):
        '''expr : expr QMARK expr COLON expr'''
        p[0] = TernaryOperationNode(condition=p[1], true_expr=p[3], false_expr=p[5], lineno=self.lexer.lineno)
        p[0].type = p[3].type
        return p[0]

    def p_expr_binary_math(self, p):
        '''expr : expr PLUS expr
                | expr MINUS expr
                | expr MULTIPLY expr
                | expr DIVIDE expr'''
        p[0] = BinaryOperationNode(expr1=p[1], expr2=p[3], operator=p[2], lineno=self.lexer.lineno)

    def p_expr_comparison(self, p):
        '''expr : expr GREATER_THAN expr
                | expr LESS_THAN expr
                | expr EQEQ expr
                | expr GTEQ expr
                | expr LTEQ expr
                | expr NEQ expr'''
        p[0] = ComparisonOperationNode(expr1=p[1], expr2=p[3], operator=p[2], lineno=self.lexer.lineno)


    def p_expr_not(self, p):
        '''expr : NOT expr'''
        p[0] = UnaryOperationNode(operator='!', expr=p[2], lineno=self.lexer.lineno)
        p[0].type = 'BOOL'
        return p[0]
    
    def p_expr_unary_minus(self, p):
        '''expr : MINUS expr'''
        p[0] = UnaryOperationNode(operator='-', expr=p[2], lineno=self.lexer.lineno)
        p[0].type = 'INT'  # Assuming the result is an integer
        return p[0]
    
    def p_expr_logical_and(p):
        "expr : expr AND expr"
        p[0] = BinaryOperationNode(p[1], '&&', p[3])

    def p_expr_logical_or(p):
        "expr : expr OR expr"
        p[0] = BinaryOperationNode(p[1], '||', p[3])


    def p_expr_list(self, p):
        '''expr : ID LPAREN expr RPAREN'''
        if p[1] == 'list':
            p[0] = FunctionCallNode(iden='list', clist=ClistNode(expr=[p[3]], lineno=self.lexer.lineno), lineno=self.lexer.lineno)
        elif p[1] == 'length':
            p[0] = FunctionCallNode(iden='length', clist=ClistNode(expr=[p[3]], lineno=self.lexer.lineno), lineno=self.lexer.lineno)
        else:
            p[0] = self._handle_func_call(p[1], ClistNode(expr=[p[3]], lineno=self.lexer.lineno), p[4])
        return p[0]

    def p_expr_func_call(self, p):
        '''expr : ID LPAREN clist RPAREN'''
        p[0] = self._handle_func_call(p[1], p[3], p[4])
        return p[0]

    def _handle_func_call(self, iden, args, rparen, lineno=None):
        if lineno is None:
            lineno = self.lexer.lineno
        node = FunctionCallNode(iden=iden, clist=args, lineno=lineno)
        return node

    def p_expr_iden(self, p):
        '''expr : ID'''
        p[0] = IdentifierNode(iden_value=p[1], lineno=self.lexer.lineno)
        return p[0]

    def p_expr_number(self, p):
        '''expr : NUMBER'''
        p[0] = NumberNode(num_value=p[1], lineno=self.lexer.lineno)
        p[0].type = 'INT'
        return p[0]

    def p_expr_string(self, p):
        '''expr : STRING
                | MSTRING'''
        p[0] = StringNode(str_value=p[1], lineno=self.lexer.lineno)
        p[0].type = 'STR' if p[1][0] == '"' else 'MSTR'
        return p[0]

    def p_expr_bool(self, p):
        '''expr : TRUE
                | FALSE'''
        p[0] = BooleanNode(value=p[1], lineno=self.lexer.lineno)
        p[0].type = 'BOOL'
        return p[0]

    def p_expr_null(self, p):
        '''expr : NULL'''
        p[0] = NullNode(lineno=self.lexer.lineno)
        p[0].type = 'NULL'
        return p[0]

    def p_expr_parens(self, p):
        '''expr : LPAREN expr RPAREN'''
        self.paren_count += 1
        p[0] = ParenthesisNode(expr=p[2], lineno=self.lexer.lineno)
        self.paren_count -= 1
        return p[0]
    

    def p_error(self, p):
        self.has_syntax_error = True
        print("❌ Syntax Errors:")
        if self.paren_count > 0:
            print(f"Error: Unmatched opening parentheses at line {self.lexer.lineno}.")
        if self.brace_count > 0:
            print(f"Error: Unmatched curly braces at line {self.lexer.lineno}.")
        if p:
            if p.type in tokens:
                print(f"Maybe you forgot to put ; before '{p.value}' at line {self.lexer.lineno}")
            else:    
                print(f"Syntax error at token: '{p.value}' at line {self.lexer.lineno}")
        else:
            print(f"Syntax error at EOF")

            