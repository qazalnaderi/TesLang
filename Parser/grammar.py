from Lexer.tokens import tokens
from .ast import *


class Grammar:
    def __init__(self, lexer):
        self.lexer = lexer

# prog :=
    def p_prog1(self, p):
        '''prog : empty'''
        p[0] = ProgramNode(function=EmptyNode(
            self.lexer.lineno), prog=None, lineno=self.lexer.lineno)
        return p[0]

    def p_prog_func(self, p):
        '''prog : func prog'''
        p[0] = ProgramNode(function=p[1], prog=p[2], lineno=self.lexer.lineno)
        return p[0]

# func :=

    def p_func_with_body(self, p):
        '''func : FUNK iden LPAREN flist RPAREN type LBRACE body RBRACE'''
        p[0] = FunctionNode(type=p[6], iden=p[2], flist=p[4],
                            func_choice=p[7], lineno=self.lexer.lineno)
        return p[0]

    def p_func_without_body(self, p):
        '''func : FUNK iden LPAREN flist RPAREN type ARROW RETURN expr SEMI'''
        p[0] = FunctionWithReturnNode(
            type=p[6], iden=p[2], flist=p[4], return_expr=p[8], lineno=self.lexer.lineno)
        return p[0]

    def p_stmt_expr(self, p):
        '''stmt : expr SEMI'''
        p[0] = ExpressionStatementNode(expr=p[1], linen=self.lexer.lineno)
        return p[0]

# stmt :=
    # defvar :=
    def p_stmt_defvar(self, p):
        '''stmt : defvar SEMI'''

        if len(p) == 4:
            # defvar := iden :: type = expr
            p[0] = VariableDefinitionNode(
                defvar_choice=p[3], lineno=self.lexer.lineno)
        else:
            # defvar := iden :: type
            p[0] = VariableDefinitionNode(
                defvar_choice=p[2], lineno=self.lexer.lineno)
        return p[0]

    def p_stmt_func(self, p):
        '''stmt : func SEMI'''
        p[0] = FunctionNode(iden=p[1], lineno=self.lexer.lineno)
        return p[0]

    def p_stmt_if(self, p):
        '''stmt : IF LPAREN expr RPAREN stmt'''
        p[0] = IfStatementNode(condition=p[3], stmt=p[5],
                               lineno=self.lexer.lineno)
        return p[0]

    def p_stmt_if_else(self, p):
        '''stmt : IF LPAREN expr RPAREN stmt ELSE stmt'''
        p[0] = IfStatementNode(condition=p[3], stmt=p[5],
                               lse_stmt=p[7], lineno=self.lexer.lineno)
        return p[0]

    def p_stmt_while(self, p):
        '''stmt : WHILE LPAREN expr RPAREN stmt'''
        p[0] = WhileStatementNode(
            condition=p[3], stmt=p[5], lineno=self.lexer.lineno)
        return p[0]

    def p_stmt_do_while(self, p):
        '''stmt : DO stmt WHILE LPAREN expr RPAREN'''
        p[0] = DoWhileStatementNode(
            stmt=p[2], condition=p[5], lineno=self.lexer.lineno)
        return p[0]

    def p_stmt_for(self, p):
        '''stmt : FOR LPAREN iden EQUAL expr TO expr RPAREN stmt'''
        p[0] = ForStatementNode(iden=p[3], expr1=p[5],
                                expr2=p[7], stmt=p[9], lineno=self.lexer.lineno)
        return p[0]

    def p_stmt_begin_end(self, p):
        '''stmt : BEGIN body END'''
        p[0] = BodyNode(body=p[2], lineno=self.lexer.lineno)
        return p[0]

    def p_stmt_return(self, p):
        '''stmt : RETURN expr SEMI'''
        p[0] = ReturnStatementNode(expr=p[2], lineno=self.lexer.lineno)
        return p[0]


# flist :=


    def p_flist(self, p):
        '''flist : iden AS type | iden AS type COMMA flist'''
        if len(p) == 4:
            # flist : iden AS type
            p[0] = FlistNode(p[1], p[3], lineno=self.lexer.lineno)
        elif len(p) == 6:
            # iden AS type COMMA flist
            p[0] = FlistNode(p[1], p[3], p[5], lineno=self.lexer.lineno)
        return p[0]


# clist :=

    def p_clist(self, p):
        '''clist : expr | expr COMMA clist'''

        if len(p) == 2:
            # clist : expr
            p[0] = ClistNode(expr=p[1], lineno=self.lexer.lineno)
        elif len(p) == 4:
            # expr COMMA clist
            p[0] = ClistNode(expr=p[1], next_expr=p[3],
                             lineno=self.lexer.lineno)
        return p[0]

# type :=
    def p_type(self, p):
        '''type : int | vector | str | mstr | bool | null'''
        p[0] = TypeNode(type_value=p[1], lineno=self.lexer.lineno)
        return p[0]

# expr :=

    def p_expr_array_indexing(self, p):
        '''expr : expr LBRACK expr RBRACK'''
        p[0] = ArrayIndexingNode(
            array_expr=p[1], index_expr=p[3], lineno=self.lexer.lineno)
        return p[0]

    def p_expr_clist(self, p):
        '''expr : LBRACK clist RBRACK'''
        p[0] = ClistNode(expr=p[2], lineno=self.lexer.lineno)
        return p[0]

    def p_expr_ternary(self, p):
        '''expr : expr QUESTION expr COLON expr'''
        p[0] = TernaryOperationNode(p[1], p[3], p[5], self.lexer.lineno)
        return p[0]

    def p_expr_add(self, p):
        '''expr : expr PLUS expr'''
        p[0] = BinaryOperationNode(p[1], p[3], '+', self.lexer.lineno)
        return p[0]

    def p_expr_sub(self, p):
        '''expr : expr MINUS expr'''
        p[0] = BinaryOperationNode(p[1], p[3], '-', self.lexer.lineno)
        return p[0]

    def p_expr_mul(self, p):
        '''expr : expr TIMES expr'''
        p[0] = BinaryOperationNode(p[1], p[3], '*', self.lexer.lineno)
        return p[0]

    def p_expr_div(self, p):
        '''expr : expr DIVIDE expr'''
        p[0] = BinaryOperationNode(p[1], p[3], '/', self.lexer.lineno)
        return p[0]

    def p_expr_gt(self, p):
        '''expr : expr GREATER expr'''
        p[0] = ComparisonOperationNode(p[1], p[3], '>', self.lexer.lineno)
        return p[0]

    def p_expr_lt(self, p):
        '''expr : expr LESS expr'''
        p[0] = ComparisonOperationNode(p[1], p[3], '<', self.lexer.lineno)
        return p[0]

    def p_expr_eq(self, p):
        '''expr : expr EQUALS expr'''
        p[0] = ComparisonOperationNode(p[1], p[3], '==', self.lexer.lineno)
        return p[0]

    def p_expr_ge(self, p):
        '''expr : expr GREATER_EQUAL expr'''
        p[0] = ComparisonOperationNode(p[1], p[3], '>=', self.lexer.lineno)
        return p[0]

    def p_expr_le(self, p):
        '''expr : expr LESS_EQUAL expr'''
        p[0] = ComparisonOperationNode(p[1], p[3], '<=', self.lexer.lineno)
        return p[0]

    def p_expr_ne(self, p):
        '''expr : expr NOT_EQUAL expr'''
        p[0] = ComparisonOperationNode(p[1], p[3], '!=', self.lexer.lineno)
        return p[0]

    def p_expr_or(self, p):
        '''expr : expr OR expr'''
        p[0] = BinaryOperationNode(p[1], p[3], '||', self.lexer.lineno)
        return p[0]
    
    def p_expr_and(self, p):
        '''expr : expr AND expr'''
        p[0] = BinaryOperationNode(p[1], p[3], '&&', self.lexer.lineno)
        return p[0]

    def p_expr_iden(self, p):
        '''expr : iden'''
        p[0] = IdentifierNode(p[1], self.lexer.lineno)
        return p[0]

    def p_expr_func_call(self, p):
        '''expr : iden LPAREN clist RPAREN'''
        p[0] = FunctionCallNode(p[1], p[3], self.lexer.lineno)
        return p[0]

    def p_expr_number(self, p):
        '''expr : number'''
        p[0] = NumberNode(p[1], self.lexer.lineno)
        return p[0]

    def p_string(self, p):
        '''expr : STRING'''
        p[0] = StringNode(p[1], self.lexer.lineno)
        return p[0]
    
    def p_multiline_string(self, p):
        '''expr : MULTILINE_STRING'''
        p[0] = StringNode(p[1], self.lexer.lineno)
        return p[0]
