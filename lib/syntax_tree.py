from .tokens import Token
from os.path import exists

class IntegerStatement():
    def __init__(self, tokeninfo):
        self.value = tokeninfo.value

    def __str__(self):
        return f"{self.value}"

    def eval(self, env, lexer):
        try:
            return float(self.value) if "." in self.value else int(self.value)
        except ValueError:
            lexer.raise_error(f"{self.value} is not a valid integer", exception="ValueError")

class ImportStatement():
    def __init__(self, address: list):
        self.value = [a.value for a in address]

    def __repr__(self):
        return f"IMPORT : {self.value}"

    def eval(self, env, lexer):
        # TODO: process function
        for address in self.value:
            if not exists(address):
                lexer.raise_error(f"{address} does not exist", exception="FileNotFoundError")

class StringStatement():
    def __init__(self, tokeninfo):
        self.value = tokeninfo.value

    def __repr__(self):
        return f"`{self.value}`"

    def eval(self, env, lexer):
        try:
            return str(self.value) 
        except ValueError:
            lexer.raise_error(f"{self.value} is not a string integer", exception="ValueError")
                   
class BooleanStatement():
    def __init__(self, tokeninfo):
        self.token = tokeninfo.token

    def eval(self, env, lexer):
        return True if self.token == Token.TRUE else False

class AssignmentStatment():
    def __init__(self, token, expression, *, is_global):
        self.variable_name = token.value
        self.expression = expression
        self.is_global = is_global
    
    def __repr__(self):
        return f"{'GLOBAL_ASSIGN' if self.is_global else 'ASSIGN'} {self.variable_name} = {self.expression}"
        
    def eval(self,  env, lexer):
        env.store_value(self.variable_name, self.expression.eval(env, lexer), is_global=self.is_global)

class BlockStatement:
    def __init__(self, block: list):
        self.block = block
       
    def __repr__(self):
        return "\n\t".join([x.__repr__() for x in self.block])
        
    def eval(self,  env, lexer):
        for block in self.block:
            block.eval(env, lexer)
        
class ScenarioStatement:
    def __init__(self, test_name, block: list):
        self.block = block
        self.test_name = test_name.value
    
    def __repr__(self):
        return f"SCENARIO {self.test_name} {self.block}"

    def eval(self,  env, lexer):
        self.block.eval(env, lexer)
        