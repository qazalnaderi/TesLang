from Lexer.lexer import print_tokens

if __name__ == '__main__':
    with open("./tests/test_input.tes", "r") as f:
        code = f.read()
    print_tokens(code)
