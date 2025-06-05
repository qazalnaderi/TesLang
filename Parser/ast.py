from anytree import NodeMixin


class Node(object):
    def accept(self, visitor, table=None):
        return visitor.visit(self)

    def setParent(self, parent):
        self.parent = parent

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class ASTNode(NodeMixin):
    def __init__(self, name, id, children=None):
        self.name = name
        self.id = id
        if children:
            self.children = children


class ProgramNode(Node):
    def __init__(self, function, prog, lineno):
        self.lineno = lineno
        self.function = function
        self.prog = prog
        self.children = (function, prog)

    def __repr__(self):
        return f"{self.__class__.__name__}(function={self.function.__repr__()}, prog={self.prog.__repr__()}, lineno={self.lineno})"


class FunctionNode(Node):
    def __init__(self, type, iden, flist, func_choice, lineno):
        self.lineno = lineno
        self.type = type
        self.iden = iden
        self.flist = flist
        self.func_choice = func_choice
        self.children = (type, iden, flist, func_choice)

    def __repr__(self):
        return f"{self.__class__.__name__}(type={self.type.__repr__()}, iden={self.iden.__repr__()}, flist={self.flist.__repr__()}, func_choice={self.func_choice.__repr__()}, lineno={self.lineno})"


class FunctionWithBodyNode(Node):
    def __init__(self, body, lineno):
        self.lineno = lineno
        self.body = body
        self.children = (body,)

    def __repr__(self):
        return f"{self.__class__.__name__}(body={self.body.__repr__()}, lineno={self.lineno})"


class FunctionWithReturnNode(Node):
    def __init__(self, expr, lineno):
        self.lineno = lineno
        self.expr = expr
        self.children = (expr,)

    def __repr__(self):
        return f"{self.__class__.__name__}(expr={self.expr.__repr__()}, lineno={self.lineno})"


class FunctionBodyNode(Node):
    def __init__(self, stmt, body, lineno):
        self.lineno = lineno
        self.stmt = stmt
        self.body = body
        self.children = (stmt, body,)

    def __repr__(self):
        return f"{self.__class__.__name__}(stmt={self.stmt.__repr__()}, body={self.body.__repr__()}, lineno={self.lineno})"


class ExpressionStatementNode(Node):
    def __init__(self, expr, lineno):
        self.lineno = lineno
        self.expr = expr
        self.children = (expr,)

    def __repr__(self):
        return f"{self.__class__.__name__}(expr={self.expr.__repr__()}, lineno={self.lineno})"


class VariableDefinitionNode(Node):
    def __init__(self, type, iden, defvar_choice, lineno):
        self.lineno = lineno
        self.type = type
        self.iden = iden
        self.defvar_choice = defvar_choice
        self.children = (type, iden, defvar_choice)

    def __repr__(self):
        return f"{self.__class__.__name__}(type={self.type.__repr__()}, iden={self.iden.__repr__()}, defvar_choice={self.defvar_choice.__repr__()}, lineno={self.lineno})"


class IfStatementNode(Node):
    def __init__(self, expr, stmt, else_choice, lineno):
        self.lineno = lineno
        self.expr = expr
        self.stmt = stmt
        self.else_choice = else_choice
        self.children = (expr, stmt, else_choice,)

    def __repr__(self):
        return f"{self.__class__.__name__}(expr={self.expr.__repr__()}, stmt={self.stmt.__repr__()}, else_choice={self.else_choice.__repr__()})"


class WhileStatementNode(Node):
    def __init__(self, expr, stmt, lineno):
        self.lineno = lineno
        self.expr = expr
        self.stmt = stmt
        self.children = (expr, stmt)

    def __repr__(self):
        return f"{self.__class__.__name__}(expr={self.expr.__repr__()}, stmt={self.stmt.__repr__()})"


class ForStatementNode(Node):
    def __init__(self, iden, expr1, expr2, stmt, lineno):
        self.lineno = lineno
        self.iden = iden
        self.expr1 = expr1
        self.expr2 = expr2
        self.stmt = stmt
        self.children = (iden, expr1, expr2, stmt)

    def __repr__(self):
        return f"{self.__class__.__name__}(iden={self.iden.__repr__()}, expr1={self.expr1.__repr__()}, expr2={self.expr2.__repr__()}, stmt={self.stmt.__repr__()})"


class ReturnStatementNode(Node):
    def __init__(self, expr, lineno):
        self.lineno = lineno
        self.expr = expr
        self.children = (expr,)

    def __repr__(self):
        return f"{self.__class__.__name__}(expr={self.expr.__repr__()})"


class IdentifierNode(Node):
    def __init__(self, iden_value, lineno):
        self.lineno = lineno
        self.iden_value = iden_value
        self.children = (iden_value,)

    def __repr__(self):
        return f"{self.__class__.__name__}(iden_value={self.iden_value.__repr__()}, lineno={self.lineno})"


class NumberNode(Node):
    def __init__(self, num_value, lineno):
        self.lineno = lineno
        self.num_value = num_value
        self.children = (num_value,)

    def __repr__(self):
        return f"{self.__class__.__name__}(num_value={self.num_value}, lineno={self.lineno})"


class StringNode(Node):
    def __init__(self, str_value, lineno):
        self.lineno = lineno
        self.str_value = str_value
        self.children = (str_value,)

    def __repr__(self):
        return f"{self.__class__.__name__}(str_value={self.str_value}, lineno={self.lineno})"


class ExpressionListNode(Node):
    def __init__(self, expr, lineno):
        self.lineno = lineno
        self.expr = expr
        self.children = (expr,)

    def __repr__(self):
        return f"{self.__class__.__name__}(expr={self.expr.__repr__()})"


class BinaryOperationNode(Node):
    def __init__(self, expr1, expr2, lineno):
        self.lineno = lineno
        self.expr1 = expr1
        self.expr2 = expr2
        self.children = (expr1, expr2)

    def __repr__(self):
        return f"BinaryOperationNode(expr1={self.expr1.__repr__()}, expr2={self.expr2.__repr__()})"


class OperatorExpressionNode(Node):
    def __init__(self, expr1, oper, expr2, lineno):
        self.lineno = lineno
        self.expr1 = expr1
        self.oper = oper
        self.expr2 = expr2
        self.children = (expr1, oper, expr2)

    def __repr__(self):
        return f"OperatorExpressionNode(expr1={self.expr1.__repr__()}, oper={self.oper.__repr__()}, expr2={self.expr2.__repr__()})"


class IdentifierExpressionNode(Node):
    def __init__(self, iden, lineno):
        self.lineno = lineno
        self.iden = iden
        self.children = (iden,)

    def __repr__(self):
        return f"IdentifierExpressionNode(iden={self.iden.__repr__()})"


class FunctionCallNode(Node):
    def __init__(self, iden, clist, lineno):
        self.lineno = lineno
        self.iden = iden
        self.clist = clist
        self.children = (iden, clist)

    def __repr__(self):
        return f"FunctionCallNode(iden={self.iden.__repr__()}, clist={self.clist.__repr__()})"


class EmptyNode(Node):
    def __init__(self, lineno):
        self.lineno = lineno
        self.name = ""
        self.children = ()

    def __repr__(self):
        return f"{self.__class__.__name__}(lineno={self.lineno})"
