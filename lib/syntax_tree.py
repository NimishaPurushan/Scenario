from .tokens import Token, INFIX_OPERATION
from os.path import exists
from os import path
from .logger import FrameworkLogger, ScenarioLogger

log = FrameworkLogger(__name__)
sc_log = ScenarioLogger(__name__)


class IntegerStatement:

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"{self.value}"

    def eval(self, env):
        try:
            return float(self.value) if "." in self.value else int(self.value)
        except ValueError:
            raise ValueError(f"{self.value} is not a valid integer")


class ImportStatement:
    immediately_execute = True

    def __init__(self, address: list):
        self.value = {a for a in address}

    def __repr__(self):
        return f"IMPORT : {self.value}"

    def eval(self, env):
        from lib.lexer import Lexer
        from lib.parser import Parser
        from lib.environment import GlobalEnv
        from lib.file_reader import FileReader
        for file_name in self.value:
            if file_name.endswith(".py"):
                if not exists(file_name):
                    sc_log.console_error(f"{file_name} does not exist")
                else:
                    _file = path.basename(file_name)
                    log.info(f"Importing File: {_file}")
                    variable_object = self._import_code(_file, file_name)
                    for o in variable_object.__dir__():
                        if not o.startswith("__"):
                            env.store_value(o, getattr(variable_object, o))
            else:
                reader = FileReader(file_name)
                try:
                    log.info(f"Importing File: {file_name}")
                    lexer = Lexer(reader)
                    parser = Parser(lexer)
                    for p in parser:
                        p.eval(env)
                except Exception as E:
                    reader.read_line()
                    sc_log.console_error(f"---------------------------------")
                    sc_log.console_error(f"File \"{file_name}\", in line {reader.line_no}, pos {reader.pos}")
                    sc_log.console_error(reader.line.decode().strip())
                    sc_log.console_error(" "*(reader.pos-1) + "^")
                    sc_log.console_error(f"{type(E).__name__}: {E}")
                    sc_log.console_error("---------------------------------")
                    env.traceback()
                    import traceback
                    traceback.print_exc()
                    exit(0)

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

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"`{self.value}`"

    def eval(self, env):
        try:
            return str(self.value) 
        except ValueError:
            raise ValueError(f"{self.value} is not a string")
                   

class BooleanStatement:

    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return "TRUE" if self.token else "FALSE"

    def eval(self, env):
        return True if self.token == Token.Truthy else False


class AssignmentStatment:

    def __init__(self, variable_name, expression):
        self.variable_name = variable_name
        self.expression = expression
    
    def __repr__(self):
        return f" {self.variable_name} = {self.expression}"
        
    def eval(self,  env):
        env.store_value(self.variable_name, self.expression.eval(env))


class BlockStatement:

    def __init__(self, block: list):
        self.block = block
       
    def __repr__(self):
        return "\t" + "\r\n\t".join([x.__repr__() for x in self.block])
        
    def eval(self,  env):
        for block in self.block:
            block.eval(env)
        

class ScenarioStatement:

    def __init__(self, test_name, block: list):
        self.block = block
        self.test_name = test_name
    
    def __repr__(self):
        return f"SCENARIO {self.test_name} {self.block}"

    def eval(self,  env):
        env.add_stack(self.test_name)
        sc_log.console(f"----------------------------------------------------------------------------")
        sc_log.console(f"SCENARIO: {self.test_name}")
        sc_log.console(f"----------------------------------------------------------------------------")
        self.block.eval(env)
        env.pop_stack()


class IfStatement:

    def __init__(self, condition, true_block, false_block: list):
        self.condition = condition
        self.true_block = true_block
        self.false_block = false_block
    
    def __repr__(self):
        return f"IF {self.condition}\nTHEN\n{self.true_block}\nELSE\n{self.false_block}\nFI"

    def eval(self,  env):
        if self.condition.eval(env):
            self.true_block.eval(env)
        else:
            self.false_block.eval(env)


class DictStatement:

    def __init__(self, variables):
        self.variables = variables

    def __repr__(self):
        return "{" + f"{[(x, y) for x,y in self.variables.items()]}"[1:-1] + "}"

    def eval(self, env):   
        return {x.eval(env): y.eval(env) for x,y in self.variables.items()}   


class DAssignmentStatement:

    def __init__(self, variable):
        self.variable = variable
     
    def __repr__(self):
        return f"${self.variable}"

    def eval(self,  env):
        return env.get_value(self.variable)
        

class ListStatement:

    def __init__(self, list_data):
        self.list_data = list_data

    def __repr__(self):
        return f"{self.list_data}"
       
    def eval(self, env):   
        return [x.eval(env) for x in self.list_data]


class FunctionStatement:

    def __init__(self, function, args: ListStatement, kargs: DictStatement):
        self.function = function
        self.kargs = kargs
        self.args = args

    def __repr__(self):
        return f"CALL {self.function.__name__}{self.args}{self.kargs}"

    def eval(self, env):   
        return self.function(*self.args.eval(env),**self.kargs.eval(env))


class InfixStatement:

    def __init__(self, lhs, op, rhs: list):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs
    
    def __repr__(self):
        return f"{self.lhs}{self.op}{self.rhs}\nFI"

    def eval(self,  env):
        return INFIX_OPERATION[self.op](self.lhs.eval(env), self.rhs.eval(env))


class CustomFunctionStatement:

    def __init__(self, function, args: ListStatement, kargs: DictStatement):
        self.function_name = function
        self.kargs = kargs
        self.args = args

    def __repr__(self):
        return f"CALL {self.function_name.__name__}{self.args}{self.kargs}"

    def eval(self, env):
        print(f"function name:", self.function_name)
        function = env.get_value(self.function_name)
        return function(*self.args.eval(env),**self.kargs.eval(env))