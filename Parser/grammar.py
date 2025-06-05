from Lexer.tokens import tokens
from .ast import *

class Grammar:
  def __init__(self, lexer):
      self.lexer = lexer


  def p_prog1(self, p):
      '''prog : empty'''
      p[0] = ProgramNode(function=EmptyNode(self.lexer.lineno), prog= None, lineno= self.lexer.lineno)
      return p[0]


  def p_prog_func(self, p):
      '''prog : func prog'''
      p[0] = ProgramNode(function=p[1], prog= p[2], lineno= self.lexer.lineno)
      return p[0]
  
  def p_func_with_body(self, p):
       '''func : FUNK iden LPAREN flist RPAREN type LBRACE body RBRACE'''
       p[0] = FunctionNode(type=p[6], iden=p[2], flist=p[4], func_choice=p[7], lineno=self.lexer.lineo)
       return p[0]
  

  def p_func_without_body(self, p):
      '''func : FUNK iden LPAREN flist RPAREN type ARROW RETURN expr SEMI'''
      p[0] = FunctionWithReturnNode(type=p[6], iden=p[2], flist=p[4], return_expr=p[8], lineno=self.lexer.lineno)
      return p[0]

      
  def p_stmt_expr(self, p):
    '''stmt : expr SEMI'''
    p[0] = ExpressionStatementNode(expr=p[1], linen=self.lexer.lineno)
    return p[0]


  def p_stmt_defvar(self, p):
    '''stmt : defvar SEMI'''
    
    if len(p) == 4:
    # defvar := iden :: type = expr     
        p[0] = VariableDefinitionNode(defvar_choice=p[3], lineno=self.lexer.lineno)
    else:
    # defvar := iden :: type     
        p[0] = VariableDefinitionNode(defvar_choice=p[2], lineno=self.lexer.lineno)
    return p[0]
    
     
  def p_stmt_func(self, p):
    '''stmt : func SEMI'''
    p[0] = FunctionNode(iden=p[1],lineno=self.lexer.lineno)
    return p[0]

  def p_stmt_if(self, p):
    '''stmt : IF LPAREN expr RPAREN stmt'''
    p[0] = IfStatementNode(condition=p[3],stmt=p[5], lineno=self.lexer.lineno)
    return p[0]


  def p_stmt_if_else(self, p):
    '''stmt : IF LPAREN expr RPAREN stmt ELSE stmt'''
    p[0] = IfStatementNode(condition=p[3], stmt=p[5], lse_stmt=p[7],lineno=self.lexer.lineno)
    return p[0]

  def p_stmt_while(self, p):
    '''stmt : WHILE LPAREN expr RPAREN stmt'''
    p[0] = WhileStatementNode(condition=p[3], stmt=p[5], lineno=self.lexer.lineno)
    return p[0]


def p_stmt_do_while(self, p):
    '''stmt : DO stmt WHILE LPAREN expr RPAREN'''
    p[0] = DoWhileStatementNode(stmt=p[2], condition=p[5],lineno=self.lexer.lineno)
    return p[0]

def p_stmt_for(self, p):
    '''stmt : FOR LPAREN iden EQUAL expr TO expr RPAREN stmt'''
    p[0] = ForStatementNode(iden=p[3], expr1=p[5], expr2=p[7], stmt=p[9], lineno=self.lexer.lineno)
    return p[0]

def p_stmt_begin_end(self, p):
    '''stmt : BEGIN body END'''
    p[0] = BodyNode(body=p[2], lineno=self.lexer.lineno)
    return p[0]

def p_stmt_return(self, p):
    '''stmt : RETURN expr SEMI'''
    p[0] = ReturnStatementNode(expr=p[2], lineno=self.lexer.lineno)
    return p[0]
