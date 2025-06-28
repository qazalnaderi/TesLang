from .symtab import *
import Parser.ast as ast
from .visitor import ASTNodeVisitor
from ply.lex import LexToken

class SemanticAnalyzer(ASTNodeVisitor):
    def __init__(self, symbol_table, semantic_messages):
        self.semantic_messages = semantic_messages
        self.global_symbol_table = symbol_table
        self.add_builtin_functions_to_table(symbol_table)
        self.function_tables = {}
        self.current_function = None

    def visit_ProgramNode(self, node, table):
        for func in node.function:
            if func is not None:
                self._check_undefined_ids(func, table, getattr(func, "lineno", 0))
                self.visit(func, table)
        if node.prog:
            self._check_undefined_ids(node.prog, table, getattr(node.prog, "lineno", 0))
            self.visit(node.prog, table)

    def visit_FunctionNode(self, node, table):
        self.current_function = node.iden
        parameters = self.extract_parameters(node.flist)
        function_name = node.iden
        function_type = node.type.type_value if node.type else "null"
        if function_type == "vector":
            function_type += " int"
        function_symbol = FunctionSymbol(function_name, function_type, parameters)
        table.put(function_symbol)
        if function_name not in self.function_tables:
            self.function_tables[function_name] = SymbolTable(table, f"{function_name}_body_symbol_table")
        function_body_table = self.function_tables[function_name]
        for param in parameters:
            param_name = param["iden_value"]
            param_type = param["type"]
            if not function_body_table.is_exist(param_name):
                if "vector" in param_type:
                    vs = VectorSymbol(param_name, param_type)
                    vs.assigned = True
                    function_body_table.put(vs)
                else:
                    vs = VariableSymbol(param_name, param_type)
                    vs.assigned = True
                    function_body_table.put(vs)
        self._check_undefined_ids(node.func_choice, function_body_table, getattr(node.func_choice, "lineno", 0))
        self.visit(node.func_choice, function_body_table)
        self.current_function = None

    def visit_BodyNode(self, node, table):
        block_table = SymbolTable(table, "block_scope")
        if isinstance(node.body, list):
            for stmt in node.body:
                self._check_undefined_ids(stmt, block_table, getattr(stmt, "lineno", 0))
                self.visit(stmt, block_table)

    def visit_IfStatementNode(self, node, table):
        self._check_undefined_ids(node.expr, table, node.lineno)
        self.visit(node.expr, table)
        self._check_undefined_ids(node.stmt, table, node.lineno)
        self.visit(node.stmt, table)
        if node.else_choice:
            self._check_undefined_ids(node.else_choice, table, node.lineno)
            self.visit(node.else_choice, table)

    def visit_WhileStatementNode(self, node, table):
        self._check_undefined_ids(node.expr, table, node.lineno)
        self.visit(node.expr, table)
        self._check_undefined_ids(node.stmt, table, node.lineno)
        self.visit(node.stmt, table)

    def visit_DoWhileStatementNode(self, node, table):
        self._check_undefined_ids(node.stmt, table, node.lineno)
        self.visit(node.stmt, table)
        self._check_undefined_ids(node.condition, table, node.lineno)
        self.visit(node.condition, table)

    def visit_ForStatementNode(self, node, table):
        loop_var = node.iden
        table.put(VariableSymbol(loop_var, "int"))
        symbol = table.get(loop_var)
        if symbol:
            symbol.assigned = True
        self._check_undefined_ids(node.expr1, table, node.lineno)
        self.visit(node.expr1, table)
        self._check_undefined_ids(node.expr2, table, node.lineno)
        self.visit(node.expr2, table)
        self._check_undefined_ids(node.stmt, table, node.lineno)
        self.visit(node.stmt, table)

    def visit_VariableDefinitionNode(self, node, table):
        name = node.iden
        type_ = node.type.type_value if node.type else "null"
        if not table.is_exist(name):
            if type_ == "vector":
                vector_type = getattr(node.type, 'vector_type_value', "int")
                sym = VectorSymbol(name, vector_type)
            else:
                sym = VariableSymbol(name, type_)
            sym.assigned = bool(node.defvar_choice)
            table.put(sym)
        if node.defvar_choice:
            self._check_undefined_ids(node.defvar_choice, table, node.lineno)
            self.visit(node.defvar_choice, table)

    def visit_AssignmentNode(self, node, table):
        self._check_undefined_ids(node.left, table, node.lineno)
        self._check_undefined_ids(node.right, table, node.lineno)
        left_name = getattr(node.left, 'iden_value', None)
        symbol = table.get(left_name) if left_name else None
        if symbol and hasattr(symbol, "assigned"):
            symbol.assigned = True
        self.visit(node.left, table)
        self.visit(node.right, table)

    def visit_ArrayIndexingNode(self, node, table):
        self._check_undefined_ids(node.array_expr, table, node.lineno)
        self._check_undefined_ids(node.index_expr, table, node.lineno)
        self.visit(node.array_expr, table)
        self.visit(node.index_expr, table)

    def visit_ComparisonOperationNode(self, node, table):
        self._check_undefined_ids(node.expr1, table, node.lineno)
        self._check_undefined_ids(node.expr2, table, node.lineno)
        self.visit(node.expr1, table)
        self.visit(node.expr2, table)

    def visit_TernaryOperationNode(self, node, table):
        self._check_undefined_ids(node.condition, table, node.lineno)
        self._check_undefined_ids(node.true_expr, table, node.lineno)
        self._check_undefined_ids(node.false_expr, table, node.lineno)
        self.visit(node.condition, table)
        self.visit(node.true_expr, table)
        self.visit(node.false_expr, table)

    def visit_UnaryOperationNode(self, node, table):
        self._check_undefined_ids(node.expr, table, node.lineno)
        self.visit(node.expr, table)

    def visit_FunctionCallNode(self, node, table):
        if node.clist:
            self._check_undefined_ids(node.clist, table, node.lineno)
        func_name = node.iden
        symbol = table.get(func_name) or (table.parent.get(func_name) if table.parent else None)
        if not symbol:
            self.semantic_messages.add_message(
                {"message": f"function '{func_name}' is not defined", "lineno": node.lineno})
            return
        expected_params = symbol.parameters
        actual_args = []
        if node.clist:
            actual_args = self.visit(node.clist, table) or []
            if not isinstance(actual_args, list):
                actual_args = [actual_args]
        if len(actual_args) < len(expected_params):
            self.semantic_messages.add_message(
                {"message": f"function '{func_name}': expects {len(expected_params)} arguments but got {len(actual_args)}.", "lineno": node.lineno})
        if len(actual_args) > len(expected_params):
            self.semantic_messages.add_message(
                {"message": f"function '{func_name}': too many arguments ({len(actual_args)} given, expected {len(expected_params)})", "lineno": node.lineno})
        for i, param in enumerate(expected_params):
            if i < len(actual_args):
                expected_type = param["type"]
                arg = actual_args[i]
                actual_type = arg.get("type", "null") if arg else "null"
                if isinstance(expected_type, list):
                    if actual_type not in expected_type:
                        self.semantic_messages.add_message(
                            {"message": f"function '{func_name}': expected '{param['iden_value']}' to be of type '{expected_type}', but got '{actual_type}' instead", "lineno": node.lineno})
                else:
                    if actual_type != expected_type and not (expected_type == "vector int" and actual_type == "vector"):
                        self.semantic_messages.add_message(
                            {"message": f"function '{func_name}': expected '{param['iden_value']}' to be of type '{expected_type}', but got '{actual_type}' instead", "lineno": node.lineno})

    def visit_ClistNode(self, node, table):
        args = []
        if node.expr:
            if isinstance(node.expr, list):
                for expr in node.expr:
                    self._check_undefined_ids(expr, table, getattr(expr, "lineno", 0))
                    args.append(self.visit(expr, table))
            else:
                self._check_undefined_ids(node.expr, table, getattr(node.expr, "lineno", 0))
                args.append(self.visit(node.expr, table))
        if node.next_expr:
            next_args = self.visit(node.next_expr, table) or []
            if isinstance(next_args, list):
                args.extend(next_args)
            else:
                args.append(next_args)
        return args

    def visit_ReturnStatementNode(self, node, table):
        self._check_undefined_ids(node.expr, table, node.lineno)
        self.visit(node.expr, table)

    def visit_PrintStatementNode(self, node, table):
        self._check_undefined_ids(node.expr, table, node.lineno)
        self.visit(node.expr, table)

    def visit_NumberNode(self, node, table):
        pass

    def visit_StringNode(self, node, table):
        pass

    def visit_ParenthesisNode(self, node, table):
        self._check_undefined_ids(node.expr, table, node.lineno)
        self.visit(node.expr, table)

    def visit_BooleanNode(self, node, table):
        pass

    def visit_NullNode(self, node, table):
        pass

    def _check_undefined_ids(self, expr, table, lineno):
        from ply.lex import LexToken
        import Parser.ast as ast

        if expr is None:
            return

        if isinstance(expr, LexToken):
            if expr.type == 'ID':
                symbol = table.get(expr.value)
                if not symbol:
                    self.semantic_messages.add_message(
                        {"message": f"variable '{expr.value}' is not defined", "lineno": lineno}
                    )
                elif hasattr(symbol, "assigned") and not symbol.assigned:
                    self.semantic_messages.add_message(
                        {"message": f"Variable '{expr.value}' is used before being assigned", "lineno": lineno}
                    )
        elif hasattr(expr, 'iden_value'):
            symbol = table.get(expr.iden_value)
            if not symbol:
                self.semantic_messages.add_message(
                    {"message": f"variable '{expr.iden_value}' is not defined", "lineno": lineno}
                )
            elif hasattr(symbol, "assigned") and not symbol.assigned:
                self.semantic_messages.add_message(
                    {"message": f"Variable '{expr.iden_value}' is used before being assigned", "lineno": lineno}
                )
        elif hasattr(expr, '__dict__'):
            for value in expr.__dict__.values():
                if isinstance(value, (ast.Node, LexToken)):
                    self._check_undefined_ids(value, table, lineno)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, (ast.Node, LexToken)):
                            self._check_undefined_ids(item, table, lineno)

    def add_builtin_functions_to_table(self, table):
        table.put(FunctionSymbol(name="scan", type="int", parameters=[]))
        table.put(FunctionSymbol(name="print", type="void", parameters=[{"iden_value": "n", "type": ["int", "str", "vector int", "vector str", "null"]}]))
        table.put(FunctionSymbol(name="list", type="vector int", parameters=[{"iden_value": "x", "type": "int"}]))
        table.put(FunctionSymbol(name="length", type="int", parameters=[{"iden_value": "V", "type": ["vector int", "vector str"]}]))
        table.put(FunctionSymbol(name="exit", type="void", parameters=[{"iden_value": "n", "type": "int"}]))
        table.put(VariableSymbol(name="null", type="null"))

    def extract_parameters(self, node):
        parameters = []
        flist = node
        if isinstance(flist, LexToken) or not flist or not hasattr(flist, 'iden'):
            return parameters
        while flist:
            if hasattr(flist, 'iden') and flist.iden:
                param_type = getattr(flist.type, 'type_value', 'null')
                if param_type == "vector":
                    param_type += " int"
                parameters.append({"iden_value": flist.iden, "type": param_type})
            flist = getattr(flist, "next_param", None)
        return parameters
