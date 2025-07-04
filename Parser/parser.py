import ply.yacc as yacc

class Parser(object):
    def __init__(self, grammar):
        self.grammar = grammar
        self.lexer = grammar.lexer
        self.parser = yacc.yacc(module=grammar, debug=True) 

    def build(self, data):
        self.lexer.brace_count = 0
        self.lexer.paren_count = 0
        self.lexer.lineno = 1
        self.lexer.input(data)

        # parse می‌کنیم
        result = self.parser.parse(lexer=self.lexer, debug=False)

        # این بخش حیاتی‌ه — drain remaining tokens manually
        while True:
            tok = self.lexer.token()
            if not tok:
                break

        # حالا بررسی کنیم شمارنده‌ها صفر هستن یا نه
        if self.lexer.brace_count != 0:
            
            print(f"🔺 Error: Unmatched '{{' or '}}' (brace count = {self.lexer.brace_count})")
        if self.lexer.paren_count != 0:
            print(f"🔺 Error: Unmatched '(' or ')' (paren count = {self.lexer.paren_count})")

        return result
