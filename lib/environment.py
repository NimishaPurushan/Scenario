from logging import exception
from sys import stderr
# from .logger import FrameworkLogger
#
# log = FrameworkLogger(__name__)


class GlobalEnv:
    # format:
    # _ENV = [{
    #   "__name__": "file_name.py",
    #   "GlobalVarible": "1",
    #   "GlobalVarible": "2",
    #   },{
    #      __name__": "function_name",
    #      "__line__": 1. # position of function in name
    #      "LocalVariable": "A",
    #      "LocalVariable": "B",
    #   }]
    def __init__(self, reader):
        self.reader = reader
        self._ENV = [{}]
        self._stack_ptr = 0  # 0 pos means  global variable
        self._ENV[self._stack_ptr]["__name__"] = "main"
        self._ENV[self._stack_ptr]["__lineno__"] = 0
        self._ENV[self._stack_ptr]["__line__"] = ""
        
    def add_stack(self, function_name):
        self._ENV.append(dict())
        self._stack_ptr += 1
        self._ENV[self._stack_ptr]["__file__"] = self.reader.file_name
        self._ENV[self._stack_ptr]["__name__"] = function_name
        self._ENV[self._stack_ptr]["__lineno__"] = self.reader.line_no
        self._ENV[self._stack_ptr]["__line__"] = self.reader.line

    def store_value(self, name, value, is_global=False):
        self._ENV[0 if is_global else self._stack_ptr][name] = value
        print(self._ENV)
        
    def get_value(self, name, lexer):
        # check local stack
        print("name to search:", name)
        print("stacptr:",self._stack_ptr)
        print(self._ENV)
        if name in self._ENV[self._stack_ptr]:
            return self._ENV[self._stack_ptr][name]
        # check the last stack
        elif self._stack_ptr - 1 > 0 and name in self._ENV[self._stack_ptr]:
            return self._ENV[self._stack_ptr]
        # check if its in global variable
        elif name in self._ENV[0]:
            print("came here")
            print(type(self._ENV[0][name]))
            print(self._ENV[0][name])
            return self._ENV[0][name]
        else:
            lexer.raise_error(f"{name} does not exist", exception="NameError")

    def pop_stack(self):
        self._ENV.pop()
        self._stack_ptr -= 1

    def traceback(self):
        print("Traceback:", file=stderr)
        while len(self._ENV) > 1:
            stack     = self._ENV.pop(1)
            caller    = stack["__name__"]
            line_no   = stack["__lineno__"]
            file_name = stack["__file__"]
            print(f"File \"{file_name}\", line {line_no}, in {caller}")
            line = stack["__line__"]
            print("\t"+line)

