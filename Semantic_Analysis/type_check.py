from ply.lex import LexToken
import Parser.ast as ast
from .visitor import ASTNodeVisitor
from .symtab import *

class TypeChecker(ASTNodeVisitor):
    def __init__(self, semantic_messages):
        self.semantic_messages = semantic_messages
        self.assigned_variables = set()
        self.current_function = None

    def visit_ProgramNode(self, node, table):
        for func in node.function:
            self.visit(func, table)
        if node.prog:
            self.visit(node.prog, table)

    def visit_FunctionNode(self, node, table):
        self.current_function = node.iden
        function_type = node.type.type_value if node.type else "null"
        if function_type == "null":
            function_type = "void"
        if function_type == "vector":
            function_type += " int"
        parameters = self.extract_parameters(node.flist)
        function_symbol = table.get(node.iden)
        if not function_symbol:
            function_symbol = FunctionSymbol(node.iden, function_type, parameters=parameters)
            table.put(function_symbol)
        # پارامترها مقداردهی شده تلقی شوند
        self.assigned_variables = set([p["iden_value"] for p in function_symbol.parameters])
        function_body_table = self.find_symbol_table(f"{node.iden}_body_symbol_table", table) or table
        self.visit(node.func_choice, function_body_table)
        if isinstance(node.func_choice, ast.BodyNode) and isinstance(node.func_choice.body, list):
            for stmt in node.func_choice.body:
                if isinstance(stmt, ast.ReturnStatementNode):
                    return_type = self.visit(stmt, function_body_table)
                    if return_type and return_type["type"] != function_type and function_type != "void":
                        self.semantic_messages.add_message(
                            {"message": f"function '{self.current_function}': wrong return type. expected '{function_type}' but got '{return_type['type']}'",
                            "lineno": stmt.lineno})

    def visit_BodyNode(self, node, table):
        block_table = SymbolTable(table, "block_scope")
        if isinstance(node.body, list):
            for stmt in node.body:
                self.visit(stmt, block_table)

    def visit_VariableDefinitionNode(self, node, table):
        name = node.iden
        type_ = node.type.type_value if node.type else "null"
        if not table.is_exist(name):
            if type_ == "vector":
                vector_type = getattr(node.type, 'vector_type_value', "int")
                table.put(VectorSymbol(name, vector_type))
            else:
                table.put(VariableSymbol(name, type_))
            # اگر مقدار اولیه دارد، جزو assigned_variables باشد
            if node.defvar_choice:
                self.assigned_variables.add(name)
        if node.defvar_choice:
            expr = self.visit(node.defvar_choice, table)
            expected_type = "vector int" if type_ == "vector" else type_
            if expr and expr["type"] != expected_type and not (expected_type == "vector int" and expr["type"] == "vector"):
                self.semantic_messages.add_message(
                    {"message": f"function '{self.current_function}': variable '{name}' expected to be of type '{expected_type}' but got '{expr['type']}' instead",
                    "lineno": node.lineno})

    def visit_AssignmentNode(self, node, table):
        left_type = self.visit(node.left, table)
        right_type = self.visit(node.right, table)
        var_name = node.left.iden_value if hasattr(node.left, 'iden_value') else (
            node.left.array_expr.iden_value if isinstance(node.left, ast.ArrayIndexingNode) and hasattr(node.left.array_expr, 'iden_value') else "unknown")
        expected_type = "vector int" if isinstance(node.left, ast.ArrayIndexingNode) else left_type["type"]
        if left_type["type"] != right_type["type"]:
            self.semantic_messages.add_message(
                {"message": f"function '{self.current_function}': variable '{var_name}' expected to be of type '{expected_type}' but got '{right_type['type']}' instead",
                "lineno": node.lineno})
        if isinstance(node.left, ast.ArrayIndexingNode):
            array_type = self.visit(node.left.array_expr, table)
            if array_type["type"] != "vector int":
                self.semantic_messages.add_message(
                    {"message": f"function '{self.current_function}': variable '{var_name}' expected to be of type 'vector' but it is '{array_type['type']}' instead",
                    "lineno": node.lineno})
        # مقداردهی علامت بزن
        if hasattr(node.left, 'iden_value'):
            self.assigned_variables.add(node.left.iden_value)
        return left_type

    def visit_IdentifierNode(self, node, table):
        name = node.iden_value
        symbol = table.get(name)
        if not symbol:
            symbol = table.parent.get(name) if table.parent else None
            if not symbol:
                self.semantic_messages.add_message(
                    {"message": f"function '{self.current_function}': variable '{name}' is not defined",
                    "lineno": node.lineno})
                return {"type": "null", "id_value": name}
        if name not in self.assigned_variables:
            # بررسی کن پارامتر نباشه
            function_symbol = table.get(self.current_function) or (table.parent.get(self.current_function) if table.parent else None)
            if function_symbol:
                parameters = [p["iden_value"] for p in function_symbol.parameters]
                if name not in parameters:
                    self.semantic_messages.add_message(
                        {"message": f"function '{self.current_function}': variable '{name}' is used before being assigned",
                        "lineno": node.lineno})
        return_type = "vector int" if symbol.type == "vector int" else symbol.type
        return {"id_value": name, "type": return_type, "values_type": return_type}

    def visit_ArrayIndexingNode(self, node, table):
        array_type = self.visit(node.array_expr, table)
        index_type = self.visit(node.index_expr, table)
        var_name = node.array_expr.iden_value if hasattr(node.array_expr, 'iden_value') else "unknown"
        if array_type["type"] not in ["vector", "vector int", "vector str"]:
            self.semantic_messages.add_message(
                {"message": f"function '{self.current_function}': variable '{var_name}' expected to be of type 'vector' but it is '{array_type['type']}' instead",
                 "lineno": node.lineno})
        if index_type["type"] != "int":
            self.semantic_messages.add_message(
                {"message": f"function '{self.current_function}': array index must be 'int', got '{index_type['type']}'",
                 "lineno": node.lineno})
        return {"type": array_type["type"].split(" ")[1] if "vector" in array_type["type"] else "int", "values_type": "int"}

    def visit_FunctionCallNode(self, node, table):
        func_name = node.iden
        symbol = table.get(func_name) or (table.parent.get(func_name) if table.parent else None)
        if not symbol:
            self.semantic_messages.add_message(
                {"message": f"function '{func_name}' is not defined", "lineno": node.lineno})
            return {"type": "null", "values_type": "null"}

        expected_params = symbol.parameters
        actual_args = []
        if node.clist:
            actual_args = self.visit(node.clist, table) or []
            if not isinstance(actual_args, list):
                actual_args = [actual_args]

        if len(actual_args) < len(expected_params):
            self.semantic_messages.add_message(
                {"message": f"function '{func_name}': expects {len(expected_params)} arguments but got {len(actual_args)}.",
                "lineno": node.lineno})
            return {"type": symbol.type, "values_type": symbol.type}

        if len(actual_args) > len(expected_params):
            self.semantic_messages.add_message(
                {"message": f"function '{func_name}': too many arguments ({len(actual_args)} given, expected {len(expected_params)})",
                "lineno": node.lineno})
            return {"type": symbol.type, "values_type": symbol.type}

        for i, param in enumerate(expected_params):
            expected_type = param["type"]
            actual_type = actual_args[i].get("type", "null")
            # expected_type ممکنه لیست باشه مثل ["vector int", "vector str"]
            if isinstance(expected_type, list):
                if actual_type not in expected_type:
                    self.semantic_messages.add_message(
                        {"message": f"function '{func_name}': expected '{param['iden_value']}' to be of type '{expected_type}', but got '{actual_type}' instead",
                        "lineno": node.lineno})
            else:
                if actual_type != expected_type and not (expected_type == "vector int" and actual_type == "vector"):
                    self.semantic_messages.add_message(
                        {"message": f"function '{func_name}': expected '{param['iden_value']}' to be of type '{expected_type}', but got '{actual_type}' instead",
                        "lineno": node.lineno})

        return {"type": symbol.type, "values_type": symbol.type}


    def visit_NumberNode(self, node, table):
        if isinstance(node.num_value, float):
            self.semantic_messages.add_message(
                {"message": f"function '{self.current_function}': wrong type 'float' found. types must be one of the following 'int', 'string', 'vector'",
                "lineno": node.lineno})
            return {"type": "float", "values_type": "float"}
        return {"type": "int", "values_type": "int"}

    def visit_ParenthesisNode(self, node, table):
        return self.visit(node.expr, table)

    def visit_PrintStatementNode(self, node, table):
        expr_type = self.visit(node.expr, table)
        if expr_type["type"] not in ["int", "str", "vector", "vector int", "vector str", "null"]:
            self.semantic_messages.add_message(
                {"message": f"function '{self.current_function}': wrong type '{expr_type['type']}' found. types must be one of the following 'int', 'string', 'vector', 'null'",
                 "lineno": node.lineno})
        return expr_type

    def visit_ReturnStatementNode(self, node, table):
        return self.visit(node.expr, table)

    def visit_ForStatementNode(self, node, table):
        # متغیر حلقه مقداردهی می‌شود
        self.assigned_variables.add(node.iden)
        expr1_type = self.visit(node.expr1, table)
        expr2_type = self.visit(node.expr2, table)
        if expr1_type["type"] != "int" or expr2_type["type"] != "int":
            self.semantic_messages.add_message(
                {"message": f"function '{self.current_function}': invalid expression type in for loop range. Expected 'int'", "lineno": node.lineno})
        self.visit(node.stmt, table)

    def visit_WhileStatementNode(self, node, table):
        cond_type = self.visit(node.expr, table)
        if cond_type["type"] != "int":
            self.semantic_messages.add_message(
                {"message": f"function '{self.current_function}': while condition must be 'int'", "lineno": node.lineno})
        self.visit(node.stmt, table)

    def find_symbol_table(self, name, parent):
        for child in parent.children:
            if child.name == name:
                return child
        return parent

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
        
