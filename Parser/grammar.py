
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
        # self.defined_variables = {}  # {var: {'type': type, 'initialized': bool}}
        # self.defined_functions = {}  # {func: {'return_type': type, 'params': [(name, type), ...]}}
        self.paren_count = 0
        self.brace_count = 0
        self.current_function = None  # Track current function for return type checking

    # prog :=
    def p_prog(self, p):
        '''prog : func_list'''
        p[0] = ProgramNode(function=p[1], prog=None, lineno=self.lexer.lineno)
        return p[0]

    def p_func_list(self, p):
        '''func_list : func
                     | func func_list
                     | '''
        if len(p) == 2:
            p[0] = [p[1]] if p[1] else []
        elif len(p) == 3:
            p[0] = [p[1]] + p[2] if p[1] else p[2]
        else:
            p[0] = []
        return p[0]

    # func :=
    def p_func_with_body(self, p):
        '''func : FUNK ID LPAREN flist RPAREN LESS_THAN type GREATER_THAN LCURLYEBR body RCURLYEBR'''
        self.brace_count += 1
        self.current_function = p[2]
        param_list = []
        current = p[4]
        while current and hasattr(current, 'iden'):
            if current.iden is None or current.type is None:
                print(f"Error: Invalid parameter at line {self.lexer.lineno}")
                break
            param_list.append((current.iden, current.type.type_value))
            current = current.next_param if hasattr(current, 'next_param') else None
        # self.defined_functions[p[2]] = {'return_type': p[7].type_value, 'params': param_list}
        p[0] = FunctionNode(type=p[7], iden=p[2], flist=p[4], func_choice=p[10], lineno=self.lexer.lineno)
        self.current_function = None
        self.brace_count -= 1
        return p[0]

    def p_func_without_body(self, p):
        '''func : FUNK ID LPAREN flist RPAREN LESS_THAN type GREATER_THAN RETURN_ARROW expr SEMI_COLON'''
        self.current_function = p[2]
        param_list = []
        current = p[4]
        while current and hasattr(current, 'iden'):
            param_list.append((current.iden, current.type.type_value))
            current = current.next_param if hasattr(current, 'next_param') else None
        self.defined_functions[p[2]] = {'return_type': p[7].type_value, 'params': param_list}
        # if p[7].type_value != p[10].type:
        #     print(f"Error: Function '{p[2]}' wrong return type. Expected '{p[7].type_value}', got '{p[10].type}' at line {self.lexer.lineno}.")
        p[0] = FunctionWithReturnNode(type=p[7], iden=p[2], flist=p[4], return_expr=p[10], lineno=self.lexer.lineno)
        self.current_function = None
        return p[0]

    def p_func_error(self, p):
        '''func : error'''
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
        # if isinstance(p[1], IdentifierNode):
        #     if p[1].iden_value not in self.defined_variables:
        #         print(f"Error: Variable '{p[1].iden_value}' is not defined at line {self.lexer.lineno}.")
        #     elif self.defined_variables[p[1].iden_value]['type'] != p[3].type:
        #         print(f"Error: Type mismatch in assignment. Expected '{self.defined_variables[p[1].iden_value]['type']}', got '{p[3].type}' at line {self.lexer.lineno}.")
        #     self.defined_variables[p[1].iden_value]['initialized'] = True
        # elif isinstance(p[1], ArrayIndexingNode):
        #     if p[1].array_expr.type != 'VECTOR':
        #         print(f"Error: Expected 'VECTOR' for array indexing, got '{p[1].array_expr.type}' at line {self.lexer.lineno}.")
        #     if p[3].type != 'INT':
        #         print(f"Error: Array assignment must be of type int, got '{p[3].type}' at line {self.lexer.lineno}.")
        # else:
        #     print(f"Error: Invalid assignment target at line {self.lexer.lineno}.")
        p[0] = AssignmentNode(left=p[1], right=p[3], lineno=self.lexer.lineno)
        return p[0]
    def p_stmt_defvar(self, p):
        '''stmt : defvar SEMI_COLON'''
        # تعریف متغیر و بررسی نوع
        p[0] = VariableDefinitionNode(type=None, iden=None, defvar_choice=p[1], lineno=self.lexer.lineno)
        # if p[1].iden in self.defined_variables:
        #     print(f"Error: Variable '{p[1].iden}' is already defined at line {self.lexer.lineno}.")
        # else:
        #     self.defined_variables[p[1].iden] = {
        #         'type': p[1].type.type_value,
        #         'initialized': False
        #     }
        return p[0]

    def p_defvar(self, p):
        '''defvar : ID COLON_COLON type
                | ID COLON_COLON type EQUAL expr'''
        
        if len(p) == 4:
            p[0] = VariableDefinitionNode(iden=p[1], type=p[3],defvar_choice=None, lineno=self.lexer.lineno)
        # else:
        #     if p[3].type_value != p[5].type:
        #         print(f"Error: Type mismatch in variable definition. Expected '{p[3].type_value}', got '{p[5].type}' at line {self.lexer.lineno}.")
        #     p[0] = VariableDefinitionNode(iden=p[1], type=p[3], expr=p[5],defvar_choice=None, lineno=self.lexer.lineno)
        # if p[3].type_value == 'FLOAT':
        #     print(f"Error: Invalid type 'FLOAT' found. Types must be one of 'INT', 'STR', 'MSTR', 'VECTOR', 'BOOL', 'NULL' at line {self.lexer.lineno}.")
        return p[0]



    def p_stmt_print(self, p):
        '''stmt : PRINT expr SEMI_COLON'''
        p[0] = PrintStatementNode(expr=p[2], lineno=self.lexer.lineno)
        return p[0]

    def p_stmt_if(self, p):
        '''stmt : IF LDBLBR expr RDBLBR stmt %prec IFX'''
        # if p[3].type not in ['BOOL', 'INT']:
        #     print(f"Error: Condition in 'if' statement must be of type bool or int, got {p[3].type} at line {self.lexer.lineno}.")
        self.paren_count += 1
        p[0] = IfStatementNode(expr=p[3], stmt=p[5],else_choice=None, lineno=self.lexer.lineno)
        self.paren_count -= 1
        return p[0]

    def p_stmt_if_else(self, p):
        '''stmt : IF LPAREN expr RPAREN stmt ELSE stmt'''
        # if p[3].type not in ['BOOL', 'INT']:
        #     print(f"Error: Condition in 'if' statement must be of type bool or int, got {p[3].type} at line {self.lexer.lineno}.")
        self.paren_count += 1
        p[0] = IfStatementNode(expr=p[3], stmt=p[5], else_stmt=p[7], lineno=self.lexer.lineno)
        self.paren_count -= 1
        return p[0]

    def p_stmt_while(self, p):
        '''stmt : WHILE LPAREN expr RPAREN stmt'''
        # if p[3].type not in ['BOOL', 'INT']:
        #     print(f"Error: Condition in 'while' statement must be of type bool or int, got {p[3].type} at line {self.lexer.lineno}.")
        self.paren_count += 1
        p[0] = WhileStatementNode(condition=p[3], stmt=p[5], lineno=self.lexer.lineno)
        self.paren_count -= 1
        return p[0]

    def p_stmt_do_while(self, p):
        '''stmt : DO stmt WHILE LPAREN expr RPAREN SEMI_COLON'''
        # if p[5].type not in ['BOOL', 'INT']:
        #     print(f"Error: Condition in 'do-while' statement must be of type bool or int, got {p[5].type} at line {self.lexer.lineno}.")
        self.paren_count += 1
        p[0] = DoWhileStatementNode(stmt=p[2], condition=p[5], lineno=self.lexer.lineno)
        self.paren_count -= 1
        return p[0]

    def p_stmt_for(self, p):
        '''stmt : FOR LPAREN ID EQUAL expr TO expr RPAREN stmt'''
        # if p[5].type != 'INT' or p[7].type != 'INT':
        #     print(f"Error: For loop range should be of type int, got {p[5].type} and {p[7].type} at line {self.lexer.lineno}.")
        # if p[3] not in self.defined_variables:
        #     self.defined_variables[p[3]] = {'type': 'INT', 'initialized': True}  # Auto-initialize loop variable
        p[0] = ForStatementNode(iden=p[3], expr1=p[5], expr2=p[7], stmt=p[9], lineno=self.lexer.lineno)
        return p[0]

    def p_stmt_begin_end(self, p):
        '''stmt : BEGIN body END'''
        p[0] = BodyNode(body=p[2], lineno=self.lexer.lineno)
        return p[0]

    def p_stmt_return(self, p):
        '''stmt : RETURN expr SEMI_COLON'''
        # if self.current_function and self.defined_functions[self.current_function]['return_type'] != p[2].type:
        #     print(f"Error: Function '{self.current_function}' wrong return type. Expected '{self.defined_functions[self.current_function]['return_type']}', got '{p[2].type}' at line {self.lexer.lineno}.")
        p[0] = ReturnStatementNode(expr=p[2], lineno=self.lexer.lineno)
        return p[0]


    # flist :=
    def p_flist(self, p):
        '''flist : 
                 | ID AS type
                 | ID AS type COMMA flist'''
        if len(p) == 4:
            p[0] = FlistNode(iden=p[1], type=p[3], next_param=None, lineno=self.lexer.lineno)
    
        elif len(p) == 6:
            p[0] = FlistNode(iden=p[1], type=p[3], next_param=p[5], lineno=self.lexer.lineno)
        
        else:
            p[0] = FlistNode(iden=None, type=None, next_param=None, lineno=self.lexer.lineno)
        
        return p[0]

    # clist :=
    def p_clist(self, p):
        '''clist : expr
                 | expr COMMA clist'''
        if len(p) == 2:
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
        # if p[3].type != 'INT':
        #     print(f"Error: Array index must be of type int, got {p[3].type} at line {self.lexer.lineno}.")
        # if p[1].type != 'VECTOR':
        #     print(f"Error: Expected 'VECTOR' for array indexing, got '{p[1].type}' at line {self.lexer.lineno}.")
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
        # if p[1].type not in ['BOOL', 'INT']:
        #     print(f"Error: Condition in ternary operation must be bool or int, got {p[1].type} at line {self.lexer.lineno}.")
        # if p[3].type != p[5].type:
        #     print(f"Error: Type mismatch in ternary operation. Expected same types, got {p[3].type} and {p[5].type} at line {self.lexer.lineno}.")
        p[0] = TernaryOperationNode(condition=p[1], true_expr=p[3], false_expr=p[5], lineno=self.lexer.lineno)
        p[0].type = p[3].type
        return p[0]

    def p_expr_binary(self, p):
        '''expr : expr PLUS expr
                | expr MINUS expr
                | expr MULTIPLY expr
                | expr DIVIDE expr
                | expr GREATER_THAN expr
                | expr LESS_THAN expr
                | expr EQEQ expr
                | expr GTEQ expr
                | expr LTEQ expr
                | expr NEQ expr
                | expr OR expr
                | expr AND expr'''
        op = {
        '+': '+', '-': '-', '*': '*', '/': '/',
        '>': '>', '<': '<', '==': '==', 
        '>=': '>=', '<=': '<=', '!=': '!=', '||': '||', '&&': '&&'
    }
        
        # گرفتن عملگر از توکن‌های p[2]
        operator = op.get(p[2])
          
        if not operator:
            print(f"Error: Unknown operator {p[2]} at line {self.lexer.lineno}.")
            return None

        # # چک کردن هم‌نوع بودن عبارات در دو طرف عملگر
        # if p[1].type != p[3].type:
        #     print(f"Error: Type mismatch in {operator} operation. Expected same types, got {p[1].type} and {p[3].type} at line {self.lexer.lineno}.")
        
        # اگر عملگر مقایسه‌ای باشد
        # if operator in ['>', '<', '==', '>=', '<=', '!=', '||', '&&']:
        p[0] = ComparisonOperationNode(expr1=p[1], expr2=p[3], operator=operator, lineno=self.lexer.lineno)
            # p[0].type = 'BOOL'
        # else:
            # p[0] = BinaryOperationNode(expr1=p[1], expr2=p[3], operator=operator, lineno=self.lexer.lineno)
            # p[0].type = p[1].type  # برای سایر عملگرهای غیر مقایسه‌ای

        return p[0]

    def p_expr_not(self, p):
        '''expr : NOT expr'''
        # if p[2].type not in ['BOOL', 'INT']:
        #     print(f"Error: Operand of 'not' must be bool or int, got {p[2].type} at line {self.lexer.lineno}.")
        p[0] = UnaryOperationNode(operator='!', expr=p[2], lineno=self.lexer.lineno)
        p[0].type = 'BOOL'
        return p[0]

    def p_expr_list(self, p):
        '''expr : ID LPAREN expr RPAREN'''
        if p[1] == 'list':
            # if p[3].type != 'INT':
                # print(f"Error: 'list' function expects int size, got {p[3].type} at line {self.lexer.lineno}.")
            p[0] = FunctionCallNode(iden='list', clist=ClistNode(expr=[p[3]], lineno=self.lexer.lineno), lineno=self.lexer.lineno)
            p[0].type = 'VECTOR'
        elif p[1] == 'length':
            # if p[3].type not in ['STR', 'VECTOR']:
            #     print(f"Error: 'length' function expects str or vector, got {p[3].type} at line {self.lexer.lineno}.")
            p[0] = FunctionCallNode(iden='length', clist=ClistNode(expr=[p[3]], lineno=self.lexer.lineno), lineno=self.lexer.lineno)
            p[0].type = 'INT'
        else:
            p[0] = self._handle_func_call(p[1], ClistNode(expr=[p[3]], lineno=self.lexer.lineno), p[4])
        return p[0]

    def p_expr_func_call(self, p):
        '''expr : ID LPAREN clist RPAREN'''
        p[0] = self._handle_func_call(p[1], p[3], p[4])
        return p[0]

    # def p_expr_asint(self, p):
    #     '''expr : ASINT LPAREN expr RPAREN'''
    #     if p[3].type not in ['INT', 'NUMBER']:
    #         print(f"Error: 'asint' expects int or number, got {p[3].type} at line {self.lexer.lineno}.")
    #     p[0] = CastNode(iden='INT', expr=p[3], lineno=self.lexer.lineno)
    #     p[0].type = 'INT'
    #     return p[0]

    def _handle_func_call(self, iden, args, rparen, lineno=None):
        if lineno is None:
            lineno = self.lexer.lineno
        # if iden not in self.defined_functions:
        #     print(f"Error: Function '{iden}' is not defined at line {lineno}.")
        #     return None
        # expected_params = self.defined_functions[iden]['params']
        # given_args = args.exprs if hasattr(args, 'exprs') else [args]
        # if len(expected_params) != len(given_args):
        #     print(f"Error: Function '{iden}' expects {len(expected_params)} arguments but got {len(given_args)} at line {lineno}.")
        # for i, ((param_name, param_type), arg) in enumerate(zip(expected_params, given_args)):
        #     if arg.type != param_type:
        #         print(f"Error: Function '{iden}' expected '{param_type}' for parameter {i+1}, got '{arg.type}' at line {lineno}.")
        node = FunctionCallNode(iden=iden, clist=args, lineno=lineno)
        # node.type = self.defined_functions[iden]['return_type']
        return node

    def p_expr_iden(self, p):
        '''expr : ID'''
        # if p[1] not in self.defined_variables:
            # print(f"Error: Variable '{p[1]}' is not defined at line {self.lexer.lineno}.")
        p[0] = IdentifierNode(iden_value=p[1], lineno=self.lexer.lineno)
            # p[0].type = 'NULL'  # Default type for error recovery
        # else:
            # if not self.defined_variables[p[1]]['initialized']:
                # print(f"Error: Variable '{p[1]}' is used before being assigned at line {self.lexer.lineno}.")
            # p[0] = IdentifierNode(iden_value=p[1], lineno=self.lexer.lineno)
            # p[0].type = self.defined_variables[p[1]]['type']
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
        # if p[2] is None:
        #     print(f"Error: Invalid expression inside parentheses at line {self.lexer.lineno}")
        #     return None  # یا هر گونه خطای مورد نظر
        p[0] = ParenthesisNode(expr=p[2], lineno=self.lexer.lineno)
        # p[0].type = p[2].type
        self.paren_count -= 1
        return p[0]

    def p_error(self, p):
        if self.paren_count > 0:
            print(f"Error: Unmatched opening parentheses at line {self.lexer.lineno}.")
        if self.brace_count > 0:
            print(f"Error: Unmatched curly braces at line {self.lexer.lineno}.")
        if p:
            print(f"Syntax error at token: '{p.value}' at line {self.lexer.lineno}")
        else:
            print(f"Syntax error at EOF")

            