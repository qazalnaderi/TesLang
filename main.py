from Parser.parser import Parser
from Parser.ast import *
from Parser.grammar import Grammar
from Lexer.tokens import tokenize
from tabulate import tabulate
from SemanticAnalyzer.semantic_analyzer import SemanticAnalyzer
from IR.generator import CodeGenerator

def process_input(filename):
    with open(filename, 'r') as file:
        return file.read()


def print_tokens(tokens_list):
    table_data = []
    for token in tokens_list:
        table_data.append([token.lineno, token.column, token.type, token.value])

    headers = ["Line", "Column", "Token", "Value"]
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))


def print_symbol_table(table, indent=0):
    print("  " * indent + f"SymbolTable(name='{table.name}', symbols={table.symbols})")
    for child in table.children:
        print_symbol_table(child, indent + 1)

import subprocess

def run_tsvm(ts_file_path, input_values=""):
    process = subprocess.Popen(
        ["./tsvm.exe", ts_file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE  # این خط خیلی مهمه
    )

    stdout, stderr = process.communicate(input=input_values.encode())

    print("stdout:")
    print(stdout.decode())

    print("stderr:")
    print(stderr.decode())


def main():
    input_text = process_input("./tests/test_input2.tes")

    tokens_list = tokenize(input_text)
    print_tokens(tokens_list)

    grammar = Grammar()
    parser = Parser(grammar)

    ast_root = parser.build(input_text)
    # print('Parser ast_root:', ast_root)

    analyzer = SemanticAnalyzer()
    errors = analyzer.analyze(ast_root)
    analyzer.print_errors()
    
    codegen = CodeGenerator()

    code_lines = codegen.generate_code(ast_root)
    code_str = codegen.get_code_string()
    # codegen.print_code()

    with open("output.ts", "w") as f:
        f.write(code_str)        

    run_tsvm("output.ts", input_values="3\n4\n")
    
    

if __name__ == "__main__":
    main()