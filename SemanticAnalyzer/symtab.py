from typing import List, Optional

class SymbolTableEntry:
    """Entry in symbol table containing variable/function information"""
    def __init__(self, name: str, symbol_type: str, data_type: str = None, 
                 is_initialized: bool = False, params: List = None, 
                 return_type: str = None, lineno: int = None):
        self.name = name
        self.symbol_type = symbol_type  # 'variable' or 'function'
        self.data_type = data_type      # 'int', 'vector', 'str', etc.
        self.is_initialized = is_initialized
        self.params = params or []      # For functions: [(param_name, param_type), ...]
        self.return_type = return_type  # For functions
        self.lineno = lineno


class SymbolTable:
    """Hierarchical symbol table implementation"""
    def __init__(self, parent=None):
        self.parent = parent
        self.symbols = {}
        self.children = []
        
    def define(self, entry: SymbolTableEntry):
        """Define a new symbol in current scope"""
        self.symbols[entry.name] = entry
        
    def lookup(self, name: str) -> Optional[SymbolTableEntry]:
        """Look up symbol in current scope and parent scopes"""
        if name in self.symbols:
            return self.symbols[name]
        elif self.parent:
            return self.parent.lookup(name)
        return None
        
    def lookup_current_scope(self, name: str) -> Optional[SymbolTableEntry]:
        """Look up symbol only in current scope"""
        return self.symbols.get(name)
        
    def create_child_scope(self):
        """Create a new child scope"""
        child = SymbolTable(parent=self)
        self.children.append(child)
        return child