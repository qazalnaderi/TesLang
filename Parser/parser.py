import ply.yacc as yacc

class Parser(object):
    def __init__(self, grammar):
        # پارسر را با استفاده از گرامر مورد نظر ایجاد می‌کنیم
        self.parser = yacc.yacc(module=grammar, debug=True)  # تنظیم حالت دیباگ در صورت نیاز

    def build(self, data):
        # ورودی داده شده را به پارسر ارسال می‌کنیم
        return self.parser.parse(data, debug=False)
