from Parser.ast import *
from SemanticAnalyzer.visitor import Visitor
from abc import ABC, abstractmethod

class CodeGenerator(Visitor):
    """Code generator for TesLang that produces intermediate code for tsvm"""
    
    def __init__(self):
        self.code = []  # Generated code lines
        self.register_counter = 0  # For temporary registers
        self.label_counter = 0  # For labels
        self.current_function = None
        self.function_params = {}  # Store function parameters
        self.local_vars = {}  # Store local variables for current function
        self.global_vars = {}  # Store global variables
        
    def new_register(self):
        """Generate a new temporary register"""
        reg = f"r{self.register_counter}"
        self.register_counter += 1
        return reg
    
    def new_label(self, prefix="L"):
        """Generate a new label"""
        label = f"{prefix}{self.label_counter}"
        self.label_counter += 1
        return label
    
    def emit(self, instruction):
        """Emit an instruction"""
        self.code.append(instruction)
    
    def emit_comment(self, comment):
        """Emit a comment"""
        self.code.append(f"# {comment}")
    
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
        self.current_function = func_name
        
        # Reset register counter for each function
        self.register_counter = 1  # r0 is reserved for return value
        self.local_vars = {}
        
        # Extract parameters
        params = []
        param_regs = {}
        current_param = node.flist
        reg_num = 1  # Start from r1 for parameters
        
        while current_param:
            param_name = current_param.iden
            param_regs[param_name] = f"r{reg_num}"
            params.append((param_name, f"r{reg_num}"))
            reg_num += 1
            current_param = getattr(current_param, 'next_param', None)
        
        self.function_params[func_name] = param_regs
        
        # Generate function header
        param_comment = ", ".join([f"{name} => {reg}" for name, reg in params])
        if param_comment:
            param_comment += " & "
        self.emit(f"proc {func_name} # {param_comment}return value => r0")
        
        # Update register counter to account for parameters
        self.register_counter = reg_num
        
        # Visit function body
        if node.func_choice:
            self.visit(node.func_choice)
        
        # Ensure function ends with ret
        if not self.code or not any(self.code[-2:]):
            self.emit("mov r0, 0")
            self.emit("ret")

        
        self.current_function = None
        return None
    
    def visit_FunctionWithReturnNode(self, node):
        """Visit function with return expression"""
        # Generate code for the return expression
        result_reg = self.visit(node.expr)
        if result_reg:
            self.emit(f"mov r0, {result_reg}")
        self.emit("ret")
        return None
    
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
    
    def visit_FunctionBodyNode(self, node):
        """Visit function body node"""
        if node.stmt:
            self.visit(node.stmt)
        if node.body:
            self.visit(node.body)
        return None
    

    def visit_ParenthesisNode(self, node):
        """Visit parenthesis node (just pass through the expression)"""
        return self.visit(node.expr)

    
    def visit_VariableDefinitionNode(self, node):
        """Visit variable definition"""
        var_name = node.iden
        var_reg = self.new_register()
        self.local_vars[var_name] = var_reg
        
        # If there's initialization
        if node.defvar_choice:
            init_reg = self.visit(node.defvar_choice)
            if init_reg:
                self.emit(f"mov {var_reg}, {init_reg}")
        
        return var_reg
    
    def visit_AssignmentNode(self, node):
        """Visit assignment statement"""
        # Generate code for right side
        right_reg = self.visit(node.right)
        
        # Handle left side assignment
        if isinstance(node.left, IdentifierNode):
            var_name = node.left.iden_value
            # Get variable register
            var_reg = self.get_variable_register(var_name)
            if var_reg and right_reg:
                self.emit(f"mov {var_reg}, {right_reg}")
        
        elif isinstance(node.left, ArrayIndexingNode):
            # Handle array assignment
            array_reg = self.visit(node.left.array_expr)
            index_reg = self.visit(node.left.index_expr)
            if array_reg and index_reg and right_reg:
                self.emit(f"mov [{array_reg} + {index_reg}], {right_reg}")
        
        return right_reg
    
    def visit_IdentifierNode(self, node):
        """Visit identifier node"""
        var_name = node.iden_value
        return self.get_variable_register(var_name)
    
    def get_variable_register(self, var_name):
        """Get register for a variable"""
        # Check parameters first
        if self.current_function and var_name in self.function_params.get(self.current_function, {}):
            return self.function_params[self.current_function][var_name]
        
        # Check local variables
        if var_name in self.local_vars:
            return self.local_vars[var_name]
        
        # If not found, create new register for the variable
        reg = self.new_register()
        self.local_vars[var_name] = reg
        return reg
    
    def visit_FunctionCallNode(self, node):
        """Visit function call"""
        func_name = node.iden
        
        # Handle built-in functions
        if func_name == "scan":
            result_reg = self.new_register()
            self.emit(f"call iget, {result_reg}")
            return result_reg
        
        elif func_name == "print":
            if node.clist:
                arg_reg = self.visit(node.clist)
                if arg_reg:
                    self.emit(f"call iput, {arg_reg}")
            return None
        
        elif func_name == "length":
            if node.clist:
                arg_reg = self.visit(node.clist)
                result_reg = self.new_register()
                if arg_reg:
                    self.emit(f"len {result_reg}, {arg_reg}")
                return result_reg
        
        elif func_name == "list":
            if node.clist:
                size_reg = self.visit(node.clist)
                result_reg = self.new_register()
                if size_reg:
                    self.emit(f"call mem, {result_reg}, {size_reg}")

                return result_reg
        
        # Handle user-defined functions
        else:
            args = []
            if node.clist:
                args = self.collect_arguments(node.clist)
            
            result_reg = self.new_register()
            
            # Generate call instruction
            if args:
                args_str = ", ".join(args)
                self.emit(f"call {func_name}, {result_reg}, {args_str}")
            else:
                self.emit(f"call {func_name}, {result_reg}")
            
            return result_reg
    
    def collect_arguments(self, clist_node):
        """Collect function call arguments"""
        args = []
        
        if hasattr(clist_node, 'expr'):
            if isinstance(clist_node.expr, list):
                for arg in clist_node.expr:
                    arg_reg = self.visit(arg)
                    if arg_reg:
                        args.append(arg_reg)
            else:
                arg_reg = self.visit(clist_node.expr)
                if arg_reg:
                    args.append(arg_reg)
        else:
            # Single argument
            arg_reg = self.visit(clist_node)
            if arg_reg:
                args.append(arg_reg)
        
        return args
    
    def visit_ClistNode(self, node):
        """Visit call list node"""
        if hasattr(node, 'expr') and node.expr:
            return self.visit(node.expr)
        return None
    
    def visit_ArrayIndexingNode(self, node):
        """Visit array indexing"""
        array_reg = self.visit(node.array_expr)
        index_reg = self.visit(node.index_expr)
        
        if array_reg and index_reg:
            result_reg = self.new_register()
            self.emit(f"mov {result_reg}, [{array_reg} + {index_reg}]")
            return result_reg
        
        return None
    
    def visit_ReturnStatementNode(self, node):
        """Visit return statement"""
        if node.expr:
            result_reg = self.visit(node.expr)
            if result_reg:
                self.emit(f"mov r0, {result_reg}")
        else:
            self.emit("mov r0, 0")
        self.emit("ret")
        return None
    
    def visit_NumberNode(self, node):
        """Visit number literal"""
        result_reg = self.new_register()
        self.emit(f"mov {result_reg}, {node.num_value}")
        return result_reg
    
    def visit_StringNode(self, node):
        """Visit string literal"""
        result_reg = self.new_register()
        # For strings, we might need to handle them differently
        # depending on the virtual machine's string handling
        self.emit(f"mov {result_reg}, \"{node.str_value}\"")
        return result_reg
    
    def visit_BooleanNode(self, node):
        """Visit boolean literal"""
        result_reg = self.new_register()
        value = 1 if node.value else 0
        self.emit(f"mov {result_reg}, {value}")
        return result_reg
    
    def visit_NullNode(self, node):
        """Visit null literal"""
        result_reg = self.new_register()
        self.emit(f"mov {result_reg}, 0")
        return result_reg
    
    def visit_BinaryOperationNode(self, node):
        """Visit binary operation"""
        left_reg = self.visit(node.expr1)
        right_reg = self.visit(node.expr2)
        
        if not left_reg or not right_reg:
            return None
        
        result_reg = self.new_register()
        
        if node.operator == '+':
            self.emit(f"add {result_reg}, {left_reg}, {right_reg}")
        elif node.operator == '-':
            self.emit(f"sub {result_reg}, {left_reg}, {right_reg}")
        elif node.operator == '*':
            self.emit(f"mul {result_reg}, {left_reg}, {right_reg}")
        elif node.operator == '/':
            self.emit(f"div {result_reg}, {left_reg}, {right_reg}")
        elif node.operator == '%':
            self.emit(f"mod {result_reg}, {left_reg}, {right_reg}")
        else:
            # For other operations, just move left operand
            self.emit(f"mov {result_reg}, {left_reg}")
        
        return result_reg
    
    def visit_ComparisonOperationNode(self, node):
        """Visit comparison operation"""
        left_reg = self.visit(node.expr1)
        right_reg = self.visit(node.expr2)
        
        if not left_reg or not right_reg:
            return None
        
        result_reg = self.new_register()
        
        if node.operator == '==':
            self.emit(f"eq {result_reg}, {left_reg}, {right_reg}")
        elif node.operator == '!=':
            self.emit(f"ne {result_reg}, {left_reg}, {right_reg}")
        elif node.operator == '<':
            self.emit(f"lt {result_reg}, {left_reg}, {right_reg}")
        elif node.operator == '>':
            self.emit(f"gt {result_reg}, {left_reg}, {right_reg}")
        elif node.operator == '<=':
            self.emit(f"le {result_reg}, {left_reg}, {right_reg}")
        elif node.operator == '>=':
            self.emit(f"ge {result_reg}, {left_reg}, {right_reg}")
        
        return result_reg
    
    def visit_UnaryOperationNode(self, node):
        """Visit unary operation"""
        expr_reg = self.visit(node.expr)
        
        if not expr_reg:
            return None
        
        result_reg = self.new_register()
        
        if node.operator == '-':
            self.emit(f"neg {result_reg}, {expr_reg}")
        elif node.operator == '!':
            self.emit(f"not {result_reg}, {expr_reg}")
        else:
            self.emit(f"mov {result_reg}, {expr_reg}")
        
        return result_reg
    
    def visit_IfStatementNode(self, node):
        """Visit if statement"""
        condition_reg = self.visit(node.expr)
        
        if not condition_reg:
            return None
        
        else_label = self.new_label("else")
        end_label = self.new_label("endif")
        
        # Jump to else if condition is false
        self.emit(f"jz {condition_reg}, {else_label}")
        
        # Generate if body
        self.visit(node.stmt)
        
        # Jump to end
        self.emit(f"jmp {end_label}")
        
        # Else label
        self.emit(f"{else_label}:")
        
        # Generate else body if exists
        if hasattr(node, 'else_choice') and node.else_choice:
            self.visit(node.else_choice)
        
        # End label
        self.emit(f"{end_label}:")
        
        return None
    
    def visit_WhileStatementNode(self, node):
        """Visit while statement"""
        loop_label = self.new_label("while")
        end_label = self.new_label("endwhile")
        
        # Loop label
        self.emit(f"{loop_label}:")
        
        # Check condition
        condition_reg = self.visit(node.expr)
        if condition_reg:
            self.emit(f"jz {condition_reg}, {end_label}")
        
        # Generate body
        self.visit(node.stmt)
        
        # Jump back to loop
        self.emit(f"jmp {loop_label}")
        
        # End label
        self.emit(f"{end_label}:")
        
        return None
    
    def visit_ForStatementNode(self, node):
        """Visit for statement"""
        loop_var = node.iden
        loop_var_reg = self.new_register()
        self.local_vars[loop_var] = loop_var_reg
        
        # Initialize loop variable
        start_reg = self.visit(node.expr1)
        if start_reg:
            self.emit(f"mov {loop_var_reg}, {start_reg}")
        
        # Generate end value
        end_reg = self.visit(node.expr2)
        
        loop_label = self.new_label("for")
        end_label = self.new_label("endfor")
        
        # Loop label
        self.emit(f"{loop_label}:")
        
        # Check condition (loop_var < end_value)
        if end_reg:
            condition_reg = self.new_register()
            self.emit(f"lt {condition_reg}, {loop_var_reg}, {end_reg}")
            self.emit(f"jz {condition_reg}, {end_label}")
        
        # Generate body
        self.visit(node.stmt)
        
        # Increment loop variable
        self.emit(f"add {loop_var_reg}, {loop_var_reg}, 1")
        
        # Jump back to loop
        self.emit(f"jmp {loop_label}")
        
        # End label
        self.emit(f"{end_label}:")
        
        return None
    
    def visit_ExpressionStatementNode(self, node):
        """Visit expression statement"""
        return self.visit(node.expr)
    
    def visit_PrintStatementNode(self, node):
        """Visit print statement"""
        expr_reg = self.visit(node.expr)
        if expr_reg:
            self.emit(f"call iput, {expr_reg}")
        return None
    
    def generate_code(self, ast_root):
        """Main code generation method"""
        self.visit(ast_root)
        return self.code
    
    def get_code_string(self):
        """Get generated code as string"""
        return '\n'.join(self.code)
    
    def print_code(self):
        """Print generated code"""
        for line in self.code:
            print(line)

