from Parser.parser import Parser
from Parser.ast import *
from Parser.grammar import Grammar
from Lexer.tokens import tokenize
from tabulate import tabulate
from Semantic_Analysis.symtab import SymbolTable 
from Semantic_Analysis.type_check import TypeChecker
from Semantic_Analysis.analyzer import SemanticAnalyzer
from IR_Generation.IR_generator import IRGenerator  
from IR_Generation.IR_optimizer import IROptimizer
import subprocess


def process_input(filename):
    with open(filename, 'r') as file:
        return file.read()


def print_tokens(tokens_list):
    table_data = []
    for token in tokens_list:
        table_data.append([token.lineno, token.column, token.type, token.value])

    headers = ["Line", "Column", "Token", "Value"]
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

class SemanticMessages:
    def __init__(self):
        self.messages = []
    
        self.reported_set = set()  # برای جلوگیری از تکرار

    def add_message(self, message):
        # فرض بر این است که message یک dict با کلیدهای "message" و "lineno" است
        key = (message.get("message", ""))
        if key not in self.reported_set:
            self.messages.append(message)
            self.reported_set.add(key)

    
    def get_messages(self):
        return self.messages


def print_symbol_table(table, indent=0):
    print("  " * indent + f"SymbolTable(name='{table.name}', symbols={table.symbols})")
    for child in table.children:
        print_symbol_table(child, indent + 1)


# def run_tsvm(ts_file_path):
#     process = subprocess.Popen(["./tsvm.exe", ts_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     stdout, stderr = process.communicate()

#     print("stdout:")
#     print(stdout.decode())
#     print("stderr:")
#     print(stderr.decode())

# run_tsvm("output.ts")

def main():
    input_text = process_input("./tests/test_input.tes")

    tokens_list = tokenize(input_text)
    print_tokens(tokens_list)

    grammar = Grammar()
    parser = Parser(grammar)

    # Generate AST from input text
    ast_root = parser.build(input_text)
    print('Parser ast_root:', ast_root)

    # Perform semantic analysis
    semantic_messages = SemanticMessages()
    symbol_table = SymbolTable(None, "global_scope")
    semantic_analyzer = SemanticAnalyzer(symbol_table, semantic_messages)
    semantic_analyzer.visit(ast_root, symbol_table)
    print("Symbol Tables:")
    print_symbol_table(symbol_table)
    
    type_checker = TypeChecker(semantic_messages)
    type_checker.visit(ast_root, symbol_table)

    # Print semantic errors or warnings
    messages = semantic_messages.get_messages()
    if messages:
        print("Semantic Errors/Warnings:")
        for msg in sorted(messages, key=lambda x: x["lineno"]):
            print(f"Line {msg['lineno']}: {msg['message']}")
    else:
        print("Semantic analysis completed successfully with no errors.")

    # ir_generator = IRGenerator()  
    # ir_code = ir_generator.visit(ast_root, None) 
    
    # print("Generated Intermediate Code (IR):")
    # print(ir_code)

    # optimizer = IROptimizer()  # Create an optimizer
    # optimized_ir_code = optimizer.optimize(ir_code)  # Perform optimization
    # print("Optimized Intermediate Code (IR):")
    # print(optimized_ir_code)

    # # Save optimized IR code to a file
    # with open("output.ts", "w") as file:
    #     file.write(optimized_ir_code)

    # # Run tsvm on the generated IR file
    # run_tsvm("output.ts")


if __name__ == "__main__":
    main()