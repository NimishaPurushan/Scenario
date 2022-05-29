from .tokens import Token
from os.path import exists
from os import path
from .logger import FrameworkLogger, ScenarioLogger

log = FrameworkLogger(__name__)
sc_log = ScenarioLogger(__name__)


class IntegerStatement:

    def __init__(self, tokeninfo):
        self.value = tokeninfo.value

    def __str__(self):
        return f"{self.value}"

    def eval(self, env, lexer):
        try:
            return float(self.value) if "." in self.value else int(self.value)
        except ValueError:
            lexer.raise_error(f"{self.value} is not a valid integer", exception="ValueError")


class ImportStatement:

    def __init__(self, address: list):
        self.value = [a.value for a in address]

    def __repr__(self):
        return f"IMPORT : {self.value}"

    def eval(self, env, lexer):
        for address in self.value:
            if not exists(address):
                lexer.raise_error(f"{address} does not exist", exception="FileNotFoundError")
            else:
                file_name = path.basename(address)
                log.info(f"Importing File: {address}")
                variable_object = self._import_code(file_name, address)
                for o in variable_object.__dir__():
                    if not o.startswith("__"):
                        env.store_value(o, getattr(variable_object, o), True)

    @staticmethod
    def _import_code(file_name, file_path, add_to_sys_modules=1):
        import importlib.util
        spec = importlib.util.spec_from_file_location(file_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if add_to_sys_modules:
            import sys
            sys.modules[file_name] = module
        return module


class StringStatement:

    def __init__(self, tokeninfo):
        self.value = tokeninfo.value

    def __repr__(self):
        return f"`{self.value}`"

    def eval(self, env, lexer):
        try:
            return str(self.value) 
        except ValueError:
            lexer.raise_error(f"{self.value} is not a string integer", exception="ValueError")
                   

class BooleanStatement:

    def __init__(self, tokeninfo):
        self.token = tokeninfo.token

    def __repr__(self):
        return "TRUE" if self.token else "FALSE"

    def eval(self, env, lexer):
        return True if self.token == Token.TRUE else False


class AssignmentStatment:

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
        return "\t" + "\r\n\t".join([x.__repr__() for x in self.block])
        
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
        env.add_stack(self.test_name, lexer)
        sc_log.console(f"----------------------------------------------------------------------------")
        sc_log.console(f"SCENARIO: {self.test_name}")
        sc_log.console(f"----------------------------------------------------------------------------")
        self.block.eval(env, lexer)
        env.pop_stack()


class IfStatement:

    def __init__(self, condition, true_block, false_block: list):
        self.condition = condition
        self.true_block = true_block
        self.false_block = false_block
    
    def __repr__(self):
        return f"IF {self.condition}\nTHEN\n{self.true_block}\nELSE\n{self.false_block}\nFI"

    def eval(self,  env, lexer):
        if self.condition.eval(env, lexer):
            self.true_block.eval(env, lexer)
        else:
            self.false_block.eval(env, lexer)


class DictStatement:

    def __init__(self, variables):
        self.variables = variables

    def __repr__(self):
        return "{" + f"{[(x, y) for x,y in self.variables.items()]}"[1:-1] + "}"

    def eval(self, env, lexer):   
        return {x.eval(env, lexer): y.eval(env, lexer) for x,y in self.variables.items()}   


class DAssignmentStatement:

    def __init__(self, variable):
        self.variable = variable.value
     
    def __repr__(self):
        return f"${self.variable}"

    def eval(self,  env, lexer):
        return env.get_value(self.variable, lexer)
        

class FunctionStatement:

    def __init__(self, function, arguments: DictStatement):
        self.function = function
        self.arguments = arguments

    def __repr__(self):
        return f"CALL {self.function.__name__}{self.arguments}"

    def eval(self, env, lexer):   
        return self.function(**self.arguments.eval(env, lexer))


class ListStatement:

    def __init__(self, list_data):
        self.list_data = list_data

    def __repr__(self):
        return f"{self.list_data}"
       
    def eval(self, env, lexer):   
        return [x.eval(env, lexer) for x in self.list_data]
