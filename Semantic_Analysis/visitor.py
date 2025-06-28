from .symtab import *

class ASTNodeVisitor:

    def visit(self, node, symbol_table=None):
        method_name = f'visit_{node.__class__.__name__}' 

        visitor = getattr(self, method_name, self.no_need_to_visit)

        return visitor(node, symbol_table)

    def no_need_to_visit(self, node, symbol_table):
        pass
