
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
        # self.brace_count += 1
        self.current_function = p[2]
        param_list = []
        current = p[4]
        while current and hasattr(current, 'iden') and current.iden:
            param_list.append((current.iden, current.type.type_value))
            current = current.next_param if hasattr(current, 'next_param') else None
        p[0] = FunctionNode(type=p[7], iden=p[2], flist=p[4], func_choice=p[10], lineno=self.lexer.lineno)
        self.current_function = None
        # self.brace_count -= 1

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
        # if self.brace_count > 0:
        #     print(f"Error: Unmatched curly brace(s) at line {self.lexer.lineno}.")
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
    def p_stmt_func(self, p):
        '''stmt : funk'''
        p[0] = p[1]

    def p_stmt_expr(self, p):
        '''stmt : expr SEMI_COLON'''
        p[0] = ExpressionStatementNode(expr=p[1], lineno=self.lexer.lineno)
        return p[0]
    

    def p_stmt_expr_missing_semi(self, p):
        '''stmt : expr'''
        print("❌ Compilation failed due to syntax error.")
        print(f"❌ Syntax error: Missing ';' after expression at line {self.lexer.lineno}")
        self.has_syntax_error = True
        raise SyntaxError("Missing semicolon")

    def p_stmt_assign(self, p):
        '''stmt : expr EQUAL expr SEMI_COLON'''
        p[0] = AssignmentNode(left=p[1], right=p[3], lineno=self.lexer.lineno)
        return p[0]
    
    def p_stmt_assign_missing_semi(self, p):
        '''stmt : expr EQUAL expr'''
        print("❌ Compilation failed due to syntax error.")
        print(f"❌ Syntax error: Missing ';' after assignment at line {self.lexer.lineno}")
        self.has_syntax_error = True
        raise SyntaxError("Missing semicolon")

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

    def p_stmt_defvar_missing_semi(self, p):
        '''stmt : defvar'''
        print("❌ Compilation failed due to syntax error.")
        print(f"❌ Syntax error: Missing ';' after variable declaration at line {self.lexer.lineno}")
        self.has_syntax_error = True
        raise SyntaxError("Missing semicolon")
    
    def p_stmt_print(self, p):
        '''stmt : PRINT expr SEMI_COLON'''
        p[0] = PrintStatementNode(expr=p[2], lineno=self.lexer.lineno)
        return p[0]
    
    def p_stmt_print_missing_semi(self, p):
        '''stmt : PRINT expr'''
        print("❌ Compilation failed due to syntax error.")
        print(f"❌ Syntax error: Missing ';' after print at line {self.lexer.lineno}")
        self.has_syntax_error = True
        raise SyntaxError("Missing semicolon")

    def p_stmt_if(self, p):
        '''stmt : IF LDBLBR expr RDBLBR BEGIN body END %prec IFX'''
        p[0] = IfStatementNode(expr=p[3], stmt=p[6], else_choice=None, lineno=self.lexer.lineno)
        return p[0]

    def p_stmt_if_else(self, p):
        '''stmt : IF LDBLBR expr RDBLBR BEGIN body END ELSE stmt'''
        p[0] = IfStatementNode(expr=p[3], stmt=p[6], else_choice=p[9], lineno=self.lexer.lineno)
        return p[0]

    def p_stmt_while(self, p):
        '''stmt : WHILE LDBLBR expr RDBLBR BEGIN body END'''
        p[0] = WhileStatementNode(expr=p[3], stmt=p[5], lineno=self.lexer.lineno)
        return p[0]

    def p_stmt_do_while(self, p):
        '''stmt : DO stmt WHILE LDBLBR expr RDBLBR '''
        p[0] = DoWhileStatementNode(stmt=p[2], condition=p[5], lineno=self.lexer.lineno)
        return p[0]

    def p_stmt_for(self, p):
        '''stmt : FOR LPAREN ID EQUAL expr TO expr RPAREN BEGIN body END'''
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

    def p_stmt_return_missing_semi(self, p):
        '''stmt : RETURN expr
                | RETURN'''
        print("❌ Compilation failed due to syntax error.")
        print(f"❌ Syntax error: Missing ';' after return at line {self.lexer.lineno}")
        self.has_syntax_error = True
        raise SyntaxError("Missing semicolon")

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
    
    def p_expr_logical_and(self, p):
        "expr : expr AND expr"
        p[0] = BinaryOperationNode(p[1], '&&', p[3])

    def p_expr_logical_or(self, p):
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
        
        p[0] = ParenthesisNode(expr=p[2], lineno=self.lexer.lineno)
        return p[0]
    

    def p_error(self, p):
        self.has_syntax_error = True
        print("❌ Compilation failed due to syntax error.")
        
        if p:
            # Get the current token value and line number
            error_token = p.value
            line_num = p.lineno
            
            # Look at recent tokens to understand context
            context = ""
            if hasattr(self, 'recent_tokens') and self.recent_tokens:
                recent_values = [str(tok.value) for tok in self.recent_tokens[-3:]]
                context = f" (after: {' '.join(recent_values)})"
            
            # Only try typo detection for string tokens (identifiers)
            if isinstance(error_token, str) and p.type == 'ID':
                suggestion = self._find_typo_suggestion(error_token)
                
                if suggestion:
                    print(f"❌ Syntax error: Unknown identifier '{error_token}' at line {line_num}{context}")
                    print(f"   Did you mean '{suggestion}'?")
                else:
                    # Check if it looks like a statement that should start with a keyword
                    if self._looks_like_statement_start():
                        print(f"❌ Syntax error: Unexpected identifier '{error_token}' at line {line_num}")
                        print(f"   This looks like it should be a statement. Did you mean a keyword?")
                    else:
                        print(f"❌ Syntax error: Unexpected identifier '{error_token}' at line {line_num}{context}")
            else:
                # Handle non-string tokens (numbers, symbols, etc.)
                print(f"❌ Syntax error: Unexpected token '{error_token}' at line {line_num}{context}")
                # print(f"   Token type: {p.type}")
        else:
            print("❌ Syntax error: Unexpected end of file")

    def _find_typo_suggestion(self, word):
        """Find the best typo suggestion using multiple algorithms"""
        # Only process string tokens
        if not isinstance(word, str):
            return None
            
        # Define your language's keywords and common identifiers
        valid_keywords = [
            'return', 'print', 'if', 'else', 'while', 'for', 'do', 'begin', 'end',
            'funk', 'int', 'bool', 'str', 'mstr', 'vector', 'null', 'true', 'false',
            'and', 'or', 'not', 'to', 'as'
        ]
        
        best_match = None
        best_score = float('inf')
        
        for keyword in valid_keywords:
            # Calculate multiple similarity metrics
            edit_distance = self._levenshtein_distance(word.lower(), keyword.lower())
            length_penalty = abs(len(word) - len(keyword)) * 0.5
            
            # Special bonus for common patterns
            pattern_bonus = 0
            if self._has_common_typo_pattern(word, keyword):
                pattern_bonus = -1
            
            score = edit_distance + length_penalty + pattern_bonus
            
            # Only suggest if it's reasonably close
            if score < best_score and score <= max(2, len(keyword) * 0.4):
                best_score = score
                best_match = keyword
        
        return best_match
    
    def _levenshtein_distance(self, s1, s2):
        """Calculate edit distance between two strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _has_common_typo_pattern(self, typo, correct):
        """Check for common typo patterns to give bonus points"""
        # Missing letters
        if len(typo) == len(correct) - 1:
            # Check if typo is correct with one letter removed
            for i in range(len(correct)):
                if correct[:i] + correct[i+1:] == typo:
                    return True
        
        # Extra letters
        if len(typo) == len(correct) + 1:
            # Check if correct is typo with one letter removed
            for i in range(len(typo)):
                if typo[:i] + typo[i+1:] == correct:
                    return True
        
        # Adjacent character swaps
        if len(typo) == len(correct):
            for i in range(len(typo) - 1):
                if (typo[i] == correct[i+1] and 
                    typo[i+1] == correct[i] and 
                    typo[:i] == correct[:i] and 
                    typo[i+2:] == correct[i+2:]):
                    return True
        
        return False

    def _looks_like_statement_start(self):
        """Check if we're at the beginning of where a statement should be"""
        # This is a heuristic - you can improve it based on your grammar
        if hasattr(self, 'recent_tokens') and self.recent_tokens:
            last_token = self.recent_tokens[-1]
            # If we just saw a semicolon, opening brace, or are at start of function body
            return last_token.type in ['SEMI_COLON', 'LBRACE', 'RBRACE']
        return True