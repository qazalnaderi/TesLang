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


class BodyNode(Node):
    def __init__(self, body, lineno):
        self.lineno = lineno
        self.body = body
        self.children = (body,)

    def __repr__(self):
        return f"{self.__class__.__name__}(body={self.body.__repr__()}, lineno={self.lineno})"


class FlistNode(Node):
    def __init__(self, iden, type, next_param=None, lineno=None):
        self.iden = iden
        self.type = type
        self.next_param = next_param
        self.lineno = lineno
        self.children = (
            iden, type, next_param) if next_param else (iden, type)

    def __repr__(self):
        return f"{self.__class__.__name__}(iden={self.iden}, type={self.type}, next_param={self.next_param}, lineno={self.lineno})"


class ClistNode(Node):
    def __init__(self, expr, next_expr=None, lineno=None):
        self.expr = expr
        self.next_expr = next_expr
        self.lineno = lineno
        self.children = (expr, next_expr) if next_expr else (expr,)

    def __repr__(self):
        return f"{self.__class__.__name__}(expr={self.expr}, next_expr={self.next_expr}, lineno={self.lineno})"


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


class DoWhileStatementNode(Node):
    def __init__(self, stmt, condition, lineno):
        self.stmt = stmt
        self.condition = condition
        self.lineno = lineno
        self.children = (stmt, condition)

    def __repr__(self):
        return f"{self.__class__.__name__}(stmt={self.stmt.__repr__()}, condition={self.condition.__repr__()}, lineno={self.lineno})"


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
    def __init__(self, expr1, expr2,operator, lineno):
        self.lineno = lineno
        self.expr1 = expr1
        self.expr2 = expr2
        self.operator = operator
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


class TypeNode(Node):
    def __init__(self, type_value, lineno):
        self.type_value = type_value
        self.lineno = lineno
        self.children = (type_value,)

    def __repr__(self):
        return f"{self.__class__.__name__}(type_value={self.type_value}, lineno={self.lineno})"


class EmptyNode(Node):
    def __init__(self, lineno):
        self.lineno = lineno
        self.name = ""
        self.children = ()

    def __repr__(self):
        return f"{self.__class__.__name__}(lineno={self.lineno})"


class ArrayIndexingNode(Node):
    def __init__(self, array_expr, index_expr, lineno):
        self.array_expr = array_expr
        self.index_expr = index_expr
        self.lineno = lineno
        self.children = (array_expr, index_expr)

    def __repr__(self):
        return f"{self.__class__.__name__}(array_expr={self.array_expr}, index_expr={self.index_expr}, lineno={self.lineno})"


class ComparisonOperationNode(Node):
    def __init__(self, expr1, expr2, operator, lineno):
        self.expr1 = expr1
        self.expr2 = expr2
        self.operator = operator
        self.lineno = lineno
        self.children = (expr1, expr2)

    def __repr__(self):
        return f"{self.__class__.__name__}(expr1={self.expr1}, expr2={self.expr2}, operator={self.operator}, lineno={self.lineno})"


class TernaryOperationNode(Node):
    def __init__(self, condition, true_expr, false_expr, lineno):
        self.condition = condition
        self.true_expr = true_expr
        self.false_expr = false_expr
        self.lineno = lineno
        self.children = (condition, true_expr, false_expr)

    def __repr__(self):
        return f"{self.__class__.__name__}(condition={self.condition}, true_expr={self.true_expr}, false_expr={self.false_expr}, lineno={self.lineno})"


class ParenthesisNode(Node):
    def __init__(self, expr, lineno):
        self.expr = expr
        self.lineno = lineno
        self.children = (expr,)

    def __repr__(self):
        return f"{self.__class__.__name__}(expr={self.expr.__repr__()}, lineno={self.lineno})"

class BooleanNode:
    def __init__(self, value, lineno):
        self.value = value  # True یا False
        self.lineno = lineno  # شماره خطی که در آن قرار دارد

    def __repr__(self):
        return f"BooleanNode(value={self.value}, lineno={self.lineno})"

class NullNode:
    def __init__(self, lineno):
        self.value = None  # مقدار null به صورت None ذخیره می‌شود
        self.lineno = lineno  # شماره خطی که در آن قرار دارد

    def __repr__(self):
        return f"NullNode(value={self.value}, lineno={self.lineno})"
class CastNode:
    def __init__(self, iden, expr, lineno):
        self.iden = iden  # نوع داده (مثلاً 'INT')
        self.expr = expr  # عبارت برای تبدیل
        self.lineno = lineno  # شماره خط (برای دیباگ یا پیام‌های خطا)

    def __repr__(self):
        return f"CastNode(iden={self.iden}, expr={self.expr}, lineno={self.lineno})"
class UnaryOperationNode:
    def __init__(self, operator, expr, lineno):
        self.operator = operator  # عملگر (مثلاً '!')
        self.expr = expr  # عبارت برای اعمال عملگر
        self.lineno = lineno  # شماره خط

    def __repr__(self):
        return f"UnaryOperationNode(operator={self.operator}, expr={self.expr}, lineno={self.lineno})"
class PrintStatementNode:
    def __init__(self, expr, lineno):
        self.expr = expr  # عبارت برای پرینت کردن
        self.lineno = lineno  # شماره خط

    def __repr__(self):
        return f"PrintStatementNode(expr={self.expr}, lineno={self.lineno})"


class ArrayAssignmentNode:
    def __init__(self, array_expr, index_expr, value_expr, lineno):
        self.array_expr = array_expr  # آرایه
        self.index_expr = index_expr  # شاخص
        self.value_expr = value_expr  # مقدار جدید
        self.lineno = lineno  # شماره خط
        self.type = None  # نوع داده که به آرایه اختصاص داده می‌شود

    def __repr__(self):
        return f"ArrayAssignmentNode(array_expr={self.array_expr}, index_expr={self.index_expr}, value_expr={self.value_expr}, lineno={self.lineno})"

class VariableAssignmentNode:
    def __init__(self, iden, value_expr, lineno):
        self.iden = iden  # نام متغیر
        self.value_expr = value_expr  # مقدار جدید
        self.lineno = lineno  # شماره خط
        self.type = None  # نوع داده که به متغیر اختصاص داده می‌شود

    def __repr__(self):
        return f"VariableAssignmentNode(iden={self.iden}, value_expr={self.value_expr}, lineno={self.lineno})"


class AssignmentNode:
    def __init__(self, left, right, lineno):
        self.left = left  # بخش چپ (مقداردهی به متغیر یا آرایه)
        self.right = right  # بخش راست (مقدار اختصاص داده شده)
        self.lineno = lineno  # شماره خط
        self.type = None  # نوع داده که به متغیر یا آرایه اختصاص داده می‌شود

    def __repr__(self):
        return f"AssignmentNode(left={self.left}, right={self.right}, lineno={self.lineno})"
