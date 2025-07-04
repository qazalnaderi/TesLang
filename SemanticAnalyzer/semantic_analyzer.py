from Parser.ast import *
from .symtab import *
from .visitor import Visitor

class SemanticError:
    """Represents a semantic error"""
    def __init__(self, message: str, lineno: int = None, function_name: str = None):
        self.message = message
        self.lineno = lineno
        self.function_name = function_name

        
    def __str__(self):
        if self.function_name:
            return f"Error: function '{self.function_name}': {self.message}"
        return f"Error: {self.message}"
    
    def __eq__(self, other):
        """Compare errors to avoid duplicates"""
        if not isinstance(other, SemanticError):
            return False
        return (self.message == other.message and 
                self.lineno == other.lineno and 
                self.function_name == other.function_name)
    
    def __hash__(self):
        """Make errors hashable for set operations"""
        return hash((self.message, self.lineno, self.function_name))



class SemanticAnalyzer(Visitor):
    """Main semantic analyzer using visitor pattern"""
    
    def __init__(self):
        self.global_scope = SymbolTable()
        self.current_scope = self.global_scope
        self.current_function = None
        self.errors = []
        self.valid_types = {'int', 'vector', 'str', 'string', 'mstr', 'bool', 'null'}
        self.has_sem_error = False
        self._add_builtin_functions()
    

    def _add_builtin_functions(self):
        """Add built-in functions to global scope"""
        # list(size) -> vector
        list_func = SymbolTableEntry(
            name='list', 
            symbol_type='function',
            params=[('size', 'int')],
            return_type='vector'
        )
        self.global_scope.define(list_func)
        
        # length(vector) -> int
        length_func = SymbolTableEntry(
            name='length',
            symbol_type='function', 
            params=[('array', 'vector')],
            return_type='int'
        )
        self.global_scope.define(length_func)
        
        # print(any) -> null
        print_func = SymbolTableEntry(
            name='print',
            symbol_type='function',
            params=[('value', 'any')],
            return_type='null'
        )
        self.global_scope.define(print_func)

         # scan() -> int
        scan_func = SymbolTableEntry(
            name='scan',
            symbol_type='function',
            params=[],
            return_type='int'
        )
        self.global_scope.define(scan_func)

        # exit(n: int) -> null
        exit_func = SymbolTableEntry(
            name='exit',
            symbol_type='function',
            params=[('n', 'int')],
            return_type='null'
        )
        self.global_scope.define(exit_func)

        # تعریف متغیر null
        null_var = SymbolTableEntry(
            name='null',
            symbol_type='variable',
            params=[],
            return_type='null'
        )
        self.global_scope.define(null_var)
    
    def add_error(self, message: str, lineno: int = None):
        """Add a semantic error (avoiding duplicates)"""
        error = SemanticError(message, lineno, self.current_function)
        self.has_sem_error = True
        # Check for duplicates more thoroughly
        for existing_error in self.errors:
            if (existing_error.message == error.message and 
                existing_error.function_name == error.function_name):
                return  # Don't add duplicate
        self.errors.append(error)
    
    def enter_scope(self):
        """Enter a new scope"""
        self.current_scope = self.current_scope.create_child_scope()
    
    def exit_scope(self):
        """Exit current scope"""
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent
    
    def visit(self, node):
        """Main visit method that dispatches to specific visit methods"""
        if node is None:
            return None
            
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        """Generic visit for nodes without specific handlers"""
        if hasattr(node, 'children'):
            for child in node.children:
                if child:
                    self.visit(child)
        return None
    
    def visit_ProgramNode(self, node):
        """Visit program node (root)"""
        if node.function:
            if isinstance(node.function, list):
                for func in node.function:
                    self.visit(func)
            else:
                self.visit(node.function)
        return None
    
    def visit_FunctionNode(self, node):
        """Visit function definition node"""
        func_name = node.iden
        old_function = self.current_function
        self.current_function = func_name
        
        # Check return type validity
        return_type = node.type.type_value if hasattr(node.type, 'type_value') else str(node.type)
        if return_type not in self.valid_types:
            # Create the proper error message format
            valid_types_msg = ', '.join(["'int'", "'string'", "'vector'"])  # Based on expected output
            self.add_error(f"wrong type '{return_type}' found. types must be one of the following {valid_types_msg}", node.lineno)
        
        # Extract parameters
        params = []
        current_param = node.flist
        while current_param:
            param_name = current_param.iden
            param_type = current_param.type.type_value if hasattr(current_param.type, 'type_value') else str(current_param.type)
            
            # Check parameter type validity
            if param_type not in self.valid_types:
                # Create the proper error message format
                valid_types_msg = ', '.join(["'int'", "'string'", "'vector'"])  # Based on expected output
                self.add_error(f"wrong type '{param_type}' found. types must be one of the following {valid_types_msg}", current_param.lineno)
            
            params.append((param_name, param_type))
            current_param = getattr(current_param, 'next_param', None)
        
        # Define function in global scope
        func_entry = SymbolTableEntry(
            name=func_name,
            symbol_type='function',
            params=params,
            return_type=return_type,
            lineno=node.lineno
        )
        self.global_scope.define(func_entry)
        
        # Enter function scope
        self.enter_scope()
        
        # Add parameters to function scope
        for param_name, param_type in params:
            param_entry = SymbolTableEntry(
                name=param_name,
                symbol_type='variable',
                data_type=param_type,
                is_initialized=True,  # Parameters are initialized
                lineno=node.lineno
            )
            self.current_scope.define(param_entry)
        
        # Visit function body
        if node.func_choice:
            self.visit(node.func_choice)
        
        # Exit function scope
        self.exit_scope()
        self.current_function = old_function
        
        return return_type
    
    def visit_FunctionWithReturnNode(self, node):
        """Visit function with return expression"""
        func_name = node.iden
        old_function = self.current_function
        self.current_function = func_name
        
        # Check return type validity
        return_type = node.type.type_value if hasattr(node.type, 'type_value') else str(node.type)
        if return_type not in self.valid_types:
            # Create the proper error message format
            valid_types_msg = ', '.join(["'int'", "'string'", "'vector'"])  # Based on expected output
            self.add_error(f"wrong type '{return_type}' found. types must be one of the following {valid_types_msg}", node.lineno)
        
        # Extract parameters
        params = []
        current_param = node.flist
        while current_param:
            param_name = current_param.iden
            param_type = current_param.type.type_value if hasattr(current_param.type, 'type_value') else str(current_param.type)
            
            if param_type not in self.valid_types:
                # Create the proper error message format
                valid_types_msg = ', '.join(["'int'", "'string'", "'vector'"])  # Based on expected output
                self.add_error(f"wrong type '{param_type}' found. types must be one of the following {valid_types_msg}", current_param.lineno)
            
            params.append((param_name, param_type))
            current_param = getattr(current_param, 'next_param', None)
        
        # Define function in global scope
        func_entry = SymbolTableEntry(
            name=func_name,
            symbol_type='function',
            params=params,
            return_type=return_type,
            lineno=node.lineno
        )
        self.global_scope.define(func_entry)
        
        # Enter function scope
        self.enter_scope()
        
        # Add parameters to function scope
        for param_name, param_type in params:
            param_entry = SymbolTableEntry(
                name=param_name,
                symbol_type='variable',
                data_type=param_type,
                is_initialized=True,
                lineno=node.lineno
            )
            self.current_scope.define(param_entry)
        
        # Visit return expression and check type
        expr_type = self.visit(node.expr)
        if expr_type and expr_type != return_type:
            self.add_error(f"wrong return type. expected '{return_type}' but got '{expr_type}'.", node.lineno)
        
        # Exit function scope
        self.exit_scope()
        self.current_function = old_function
        
        return return_type
    
    def visit_BodyNode(self, node):
        """Visit body node"""
        if hasattr(node, 'body') and node.body:
            if isinstance(node.body, list):
                for stmt in node.body:
                    if stmt:
                        self.visit(stmt)
            else:
                self.visit(node.body)
        return None
    
    def visit_VariableDefinitionNode(self, node):
        """Visit variable definition"""
        var_name = node.iden
        var_type = node.type.type_value if hasattr(node.type, 'type_value') else str(node.type)
        
        # Check type validity
        if var_type not in self.valid_types:
            # Create the proper error message format
            valid_types_msg = ', '.join(["'int'", "'string'", "'vector'"])  # Based on expected output
            self.add_error(f"wrong type '{var_type}' found. types must be one of the following {valid_types_msg}", node.lineno)
        
        # Check if variable already defined in current scope
        if self.current_scope.lookup_current_scope(var_name):
            self.add_error(f"variable '{var_name}' is already defined in this scope.", node.lineno)
            return None
        
        # Check initialization
        is_initialized = node.defvar_choice is not None
        if is_initialized:
            init_type = self.visit(node.defvar_choice)
            if init_type and init_type != var_type:
                self.add_error(f"variable '{var_name}' expected to be of type '{var_type}' but it is '{init_type}' instead.", node.lineno)
        
        # Define variable
        var_entry = SymbolTableEntry(
            name=var_name,
            symbol_type='variable',
            data_type=var_type,
            is_initialized=is_initialized,
            lineno=node.lineno
        )
        self.current_scope.define(var_entry)
        
        return var_type
    
    def visit_AssignmentNode(self, node):
        """Visit assignment statement"""
        # Visit right side first
        right_type = self.visit(node.right)
        
        # Handle left side assignment
        if isinstance(node.left, IdentifierNode):
            var_name = node.left.iden_value
            var_entry = self.current_scope.lookup(var_name)
            
            if not var_entry:
                self.add_error(f"variable '{var_name}' is not defined.", node.lineno)
                return None
            
            if var_entry.symbol_type != 'variable':
                self.add_error(f"'{var_name}' is not a variable.", node.lineno)
                return None
            
            # Check type compatibility
            if right_type and right_type != var_entry.data_type:
                self.add_error(f"variable '{var_name}' expected to be of type '{var_entry.data_type}' but it is '{right_type}' instead.", node.lineno)
            
            # Mark as initialized
            var_entry.is_initialized = True
            
        elif isinstance(node.left, ArrayIndexingNode):
            array_type = self.visit(node.left.array_expr)
            index_type = self.visit(node.left.index_expr)
            
            if array_type and array_type != 'vector':
                self.add_error(f"expected array to be of type 'vector', but got '{array_type}' instead.", node.lineno)
            
            if index_type and index_type != 'int':
                self.add_error(f"array index must be of type 'int', but got '{index_type}' instead.", node.lineno)
        
        return right_type
    
    def visit_IdentifierNode(self, node):
        """Visit identifier node"""
        var_name = node.iden_value
        var_entry = self.current_scope.lookup(var_name)
        
        if not var_entry:
            self.add_error(f"variable '{var_name}' is not defined.", node.lineno)
            return None
        
        if var_entry.symbol_type == 'variable':
            if not var_entry.is_initialized:
                self.add_error(f"Variable '{var_name}' is used before being assigned.", node.lineno)
            return var_entry.data_type
        
        return None
    
    def visit_FunctionCallNode(self, node):
        """Visit function call"""
        func_name = node.iden
        func_entry = self.current_scope.lookup(func_name)
        
        if not func_entry:
            self.add_error(f"function '{func_name}' is not defined.", node.lineno)
            return None
        
        if func_entry.symbol_type != 'function':
            self.add_error(f"'{func_name}' is not a function.", node.lineno)
            return None
        
        # Count arguments and get their types
        actual_args = 0
        arg_types = []
        
        if node.clist:
            # Handle different argument structures
            if hasattr(node.clist, 'expr'):
                if isinstance(node.clist.expr, list):
                    actual_args = len(node.clist.expr)
                    for arg in node.clist.expr:
                        arg_type = self.visit(arg)
                        arg_types.append(arg_type)
                else:
                    actual_args = 1
                    arg_type = self.visit(node.clist.expr)
                    arg_types.append(arg_type)
            elif hasattr(node.clist, '__iter__'):
                # If clist is iterable
                for arg in node.clist:
                    actual_args += 1
                    arg_type = self.visit(arg)
                    arg_types.append(arg_type)
            else:
                # Single argument
                actual_args = 1
                arg_type = self.visit(node.clist)
                arg_types.append(arg_type)
        
        # Check argument count
        expected_params = len(func_entry.params)
        if expected_params != actual_args:
            self.add_error(f"function '{func_name}' expects {expected_params} arguments but got {actual_args}.", node.lineno)
            return func_entry.return_type
        
        # Check argument types
        for i, (expected_type, actual_type) in enumerate(zip([p[1] for p in func_entry.params], arg_types)):
            if expected_type != 'any' and actual_type and actual_type != expected_type:
                param_name = func_entry.params[i][0]
                self.add_error(f"expected '{param_name}' to be of type '{expected_type}', but got '{actual_type}' instead.", node.lineno)
        
        return func_entry.return_type
    
    def visit_ArrayIndexingNode(self, node):
        """Visit array indexing"""
        array_type = self.visit(node.array_expr)
        index_type = self.visit(node.index_expr)
        
        if array_type and array_type != 'vector':
            self.add_error(f"expected array to be of type 'vector', but got '{array_type}' instead.", node.lineno)
        
        if index_type and index_type != 'int':
            self.add_error(f"array index must be of type 'int', but got '{index_type}' instead.", node.lineno)
        
        return 'int'  # Assume vector elements are int
    
    def visit_ReturnStatementNode(self, node):
        """Visit return statement"""
        if not self.current_function:
            self.add_error("return statement outside function.", node.lineno)
            return None
        
        func_entry = self.global_scope.lookup(self.current_function)
        if not func_entry:
            return None
        
        expr_type = self.visit(node.expr)
        if expr_type and expr_type != func_entry.return_type:
            self.add_error(f"wrong return type. expected '{func_entry.return_type}' but got '{expr_type}'.", node.lineno)
        
        return expr_type
    
    def visit_NumberNode(self, node):
        """Visit number literal"""
        return 'int'
    
    def visit_StringNode(self, node):
        """Visit string literal"""
        if hasattr(node, 'type'):
            return node.type
        return 'str'
    
    def visit_BooleanNode(self, node):
        """Visit boolean literal"""
        return 'bool'
    
    def visit_NullNode(self, node):
        """Visit null literal"""
        return 'null'
    
    def visit_ComparisonOperationNode(self, node):
        """Visit comparison operation"""
        left_type = self.visit(node.expr1)
        right_type = self.visit(node.expr2)
        return 'bool'
    
    def visit_BinaryOperationNode(self, node):
        """Visit binary operation"""
        left_type = self.visit(node.expr1)
        right_type = self.visit(node.expr2)

        if node.operator in ['&&', '||']:
            if left_type != 'bool' or right_type != 'bool':
                self.add_error(f"Logical operator '{node.operator}' requires boolean operands", node)
            return 'bool'
        
        # Return appropriate type based on operation
        if hasattr(node, 'operator'):
            if node.operator in ['==', '!=', '<', '>', '<=', '>=']:
                return 'bool'
            elif node.operator in ['+', '-', '*', '/', '%']:
                return 'int'
        
        return left_type  # Default to left operand type
    
    def visit_UnaryOperationNode(self, node):
        """Visit unary operation"""
        expr_type = self.visit(node.expr)
        if node.operator == '!':
            return 'bool'
        elif node.operator == '-':
            return 'int'
        return expr_type
    
    def visit_IfStatementNode(self, node):
        """Visit if statement"""
        condition_type = self.visit(node.expr)
        if condition_type and condition_type != 'bool':
            self.add_error(f"if condition must be boolean, got '{condition_type}'.", node.lineno)
        
        self.visit(node.stmt)
        if hasattr(node, 'else_choice') and node.else_choice:
            self.visit(node.else_choice)
        
        return None
    
    def visit_WhileStatementNode(self, node):
        """Visit while statement"""
        condition_type = self.visit(node.expr)
        if condition_type and condition_type != 'bool':
            self.add_error(f"while condition must be boolean, got '{condition_type}'.", node.lineno)
        
        self.visit(node.stmt)
        return None
    
    def visit_ForStatementNode(self, node):
        """Visit for statement"""
        # Enter new scope for loop variable
        self.enter_scope()
        
        # Define loop variable
        loop_var = SymbolTableEntry(
            name=node.iden,
            symbol_type='variable',
            data_type='int',
            is_initialized=True,
            lineno=node.lineno
        )
        self.current_scope.define(loop_var)
        
        # Check range expressions
        start_type = self.visit(node.expr1)
        end_type = self.visit(node.expr2)
        
        if start_type and start_type != 'int':
            self.add_error(f"for loop start value must be int, got '{start_type}'.", node.lineno)
        
        if end_type and end_type != 'int':
            self.add_error(f"for loop end value must be int, got '{end_type}'.", node.lineno)
        
        # Visit loop body
        self.visit(node.stmt)
        
        # Exit loop scope
        self.exit_scope()
        return None
    
    def visit_ExpressionStatementNode(self, node):
        """Visit expression statement"""
        return self.visit(node.expr)
    
    def visit_PrintStatementNode(self, node):
        """Visit print statement"""
        self.visit(node.expr)
        return None
    
    def visit_ClistNode(self, node):
        """Visit call list (function arguments or array literal)"""
        if hasattr(node, 'expr') and node.expr:
            if isinstance(node.expr, list):
                for expr in node.expr:
                    self.visit(expr)
            else:
                self.visit(node.expr)
        return 'vector'
    
    def analyze(self, ast_root):
        """Main analysis method"""
        self.visit(ast_root)
        return self.errors
    
    def print_errors(self):
        print("❌ Semantic Errors:")
        for error in self.errors:
            print(error)



