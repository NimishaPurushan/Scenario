# eval is the interface to parse data
# eval takes environment and lexer
from .tokens import Token


class IntegerStatement:
    def __init__(self, tokeninfo):
        self.value = tokeninfo.value

    def eval(self, env, lexer):
        try:
            return float(self.value) if "." in self.value else int(self.value)
        except ValueError:
            lexer.raise_error(f"ValueError: {self.value} is not a valid integer")


class StringStatement:
    def __init__(self, tokeninfo):
        self.value = tokeninfo.value

    def __repr__(self):
        return f"`{self.value}`"

    def eval(self, env, lexer):
        try:
            return str(self.value) 
        except ValueError:
            lexer.raise_error(f"ValueError: {self.value} is not a string integer")


class BooleanStatement:
    def __init__(self, tokeninfo):
        self.token = tokeninfo.token

    def eval(self, env, lexer):
        return True if self.token == Token.TRUE else False


class AssignmentStatment:
    def __init__(self, token, expression, *, is_global):
        self.variable_name = token.value
        self.expression = expression
        self.is_global = is_global
    
    def __repr__(self):
        return f"ASSIGN {self.variable_name}= {self.expression}"

    def eval(self,  env, lexer):
        self.env[self.variable_name] = self.expression.eval(env, lexer)

           

