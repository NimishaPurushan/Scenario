from logging import exception
from sys import stderr

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
    def __init__(self, file_name):
        self.file_name = file_name
        self._ENV = [{}]
        self._stack_ptr = 0 # 0 pos means  global variable    
        self._ENV[self._stack_ptr]["__name__"] = "main"
        self._ENV[self._stack_ptr]["__lineno__"] = 0
        self._ENV[self._stack_ptr]["__line__"] = ""

    
        
    def add_stack(self, function_name, lexer):
        self._stack_ptr += 1
        self._ENV.append(dict())
        self._ENV[self._stack_ptr]["__name__"] = function_name
        self._ENV[self._stack_ptr]["__lineno__"] = lexer.lineno
        self._ENV[self._stack_ptr]["__line__"] = lexer.line

    def store_value(self, name, value, is_global=False):
        self._ENV[0 if is_global else self._stack_ptr][name] = value
        
    def get_value(self, name, lexer):
        # check local stack
        if name in  self._ENV[self._stack_ptr]:
            return self._ENV[self._stack_ptr]
        # check the last stack
        elif self._stack_ptr - 1 > 0 and name in self._ENV[self._stack_ptr]:
            return self._ENV[self._stack_ptr]
        # check if its in global variable
        elif name in self._ENV[0] :
            return self._ENV[0][name]
        else:
            lexer.raise_error(f"{name} does not exist", exception="NameError")

    def pop_stack(self):
        self._ENV.pop()

    def traceback(self):
        print("Traceback:", file=stderr)
        while len(self._ENV) > 0:
            stack = self._ENV.pop(0)
            caller = stack["__name__"]
            line_no = stack["__lineno__"]
            print(f"File \"{self.file_name}\", line {line_no}, in {caller}")
            line = stack["__line__"]
            print("\t"+line)

