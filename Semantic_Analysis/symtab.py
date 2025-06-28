from sys import maxsize

class Symbol:
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __repr__(self):
        return f"Symbol(name='{self.name}', type='{self.type}')"

class VariableSymbol(Symbol):
    def __init__(self, name, type):
        super().__init__(name, type)
        self.assigned = False  # اضافه شد

class VectorSymbol(VariableSymbol):
    def __init__(self, name, type, size=maxsize):
        super().__init__(name, type)
        self.size = size
        self.assigned = False  # اضافه شد

    def __repr__(self):
        return f"VectorSymbol(name='{self.name}', type='{self.type}', size={self.size})"

class FunctionSymbol(Symbol):
    def __init__(self, name, type, parameters):
        super().__init__(name, type)
        self.parameters = parameters

    def __repr__(self):
        return f"FunctionSymbol(name='{self.name}', type='{self.type}', parameters={self.parameters})"

class SymbolTable:
    def __init__(self, parent, name):
        self.symbols = {}
        self.name = name
        self.parent = parent
        self.children = []
        if parent:
            parent.children.append(self)

    def put(self, symbol):
        self.symbols[symbol.name] = symbol
        if isinstance(symbol, FunctionSymbol):
            self.children.append(SymbolTable(self, f"{symbol.name}_body_symbol_table"))

    def get(self, name):
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.get(name)
        return None

    def is_exist(self, name):
        return self.get(name) is not None

    def getParentScope(self):
        return self.parent

    def __repr__(self):
        return f"SymbolTable(name='{self.name}', symbols={self.symbols}, children={self.children})"
