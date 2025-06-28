import ply.yacc as yacc

class Parser(object):
    def __init__(self, grammar):
        self.parser = yacc.yacc(module=grammar, debug=True) 

    def build(self, data):
        return self.parser.parse(data, debug=False)
