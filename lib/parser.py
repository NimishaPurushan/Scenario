from logging import exception
from .logger import FrameworkLogger, ScenarioLogger
from .syntax_tree import *
from .tokens import Token

log = FrameworkLogger(__name__)
tc_log = ScenarioLogger(__name__)


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.token = None
        self._get_next_statement()

    def raise_error(self, message, *, exception="Exception"):
       self.lexer.raise_error(message, exception=exception)

    def next_expression(self):
        log.info(self.token)
        if self.token == Token.EOF:
            raise StopIteration()
        return (
            self._parse_values() or
            self._parse_assignment() or
            self._parse_import() or
            self._parse_scenario() or
            self._parse_if_else() or
            self._parse_function() or 
            self._parse_list_or_dict() or
            self.lexer(f"Unknown Token: {self.token}"))

    def _get_next_statement(self):
        data = self.token
        self.token = next(self.lexer)
        return data

    def _is_next_token(self, expected_token=None, expected_value=None):
        self._get_next_statement()
        if expected_token == None or  self.token != expected_token:
            self.raise_error(f"expected {expected_token} found {self.token}", exception="TypeError")
                   
        if (expected_value == None and expected_value == self.token.value ):
            self.raise_error(f"expected {expected_value} found {self.token.value}",  exception="ValueError")
        return True
    
    def _parse_list_or_dict(self):

        if self.token == Token.BRACKET:
            if self.token.value == "[":
                data = []
                while self.token.value != "]":
                    self._get_next_statement()
                    data.append(self.next_expression())
                    if not (self.token.value == "," or  self.token.value == "]"):
                        self.raise_error(f"expected \",\" or \"]\" found \"{self.token.value}\"", exception="SyntaxError")
                self._get_next_statement()
                return ListStatement(data)

            if self.token.value == "{":
                data = {}
                while self.token.value != "}":
                    self._get_next_statement()
                    key = self.next_expression()
                    if self.token.value != ":" :
                        self.raise_error(f"expected \":\" found {self.token.value}", exception="SyntaxError")
                    self._get_next_statement()
                    value = self.next_expression()
                    if key in data:
                        self.raise_error(f"duplicate argument {key}", exception="SyntaxError")
                    data[key] = value
                self._get_next_statement()
                return DictStatement(data)
           

    def _parse_function(self):
        if self.token == Token.INBUILT_FUNCTION:
            function = self.token.value
            current_line = self.lexer.lineno
            self._get_next_statement()
            arguments = {}
            while current_line == self.lexer.lineno:
                if self.token != Token.IDENTIFIER:
                    self.raise_error(f"expected {Token.IDENTIFIER} found {self.token}", exception="SyntaxError")
      
                variable_name = StringStatement(self.token)
                self._is_next_token(Token.SYMBOL)
                if self.token.value == "=" or  self.token.value == ":":
                    self._get_next_statement()
                    if variable_name in arguments:
                        self.raise_error(f"duplicate argument {variable_name}", exception="SyntaxError")
                    arguments[variable_name]  =  self.next_expression()
                else:
                    self.raise_error(f"expected \":\" or \"=\" found \"{self.token.value}\"", exception="SyntaxError")
            return FunctionStatement(function, DictStatement(arguments))

    def _parse_if_else(self):
        if self.token == Token.IF_START:
            self._get_next_statement()
            condition = self.next_expression()
            blocks_command = [
                [], # true block
                []] # false block
            ptr = 0
            while self.token != Token.IF_END:
                if self.token == Token.ELSE:
                    ptr+=1
                elif self.token == Token.EOF:
                    self.raise_error(f"unexpected \"EOF\" expected {Token.SCENARIO_END.value}", exception="SyntaxError")
                blocks_command[ptr].append(self.next_expression())
            self._get_next_statement()
            return IfStatement(condition, BlockStatement(blocks_command[False]), BlockStatement(blocks_command[True]))

    def _parse_scenario(self):
        if self.token == Token.SCENARIO_START:
            self._get_next_statement()
            if self.token.value != ":":
                self.raise_error(f"expected \":\" found \"{self.token.value}\"", exception="SyntaxError")
            self._get_next_statement()
            test_name = self.token
            blocks_command = []
            self._get_next_statement()
            while self.token != Token.SCENARIO_END:
                if self.token == Token.EOF:
                    self.raise_error(f"unexpected \"EOF\" expected \"{Token.SCENARIO_END.value}\"", exception="SyntaxError")
                blocks_command.append(self.next_expression())
            self._get_next_statement()
            return ScenarioStatement(test_name, BlockStatement(blocks_command))

    def _parse_values(self):
        if self.token == Token.INTEGER:
            data = self.token
            self._get_next_statement()
            return IntegerStatement(data)
        elif self.token == Token.STRING:
            data = self.token
            self._get_next_statement()
            return StringStatement(data)
        elif self.token == Token.FALSE or self.token == Token.TRUE:
            data = self.token
            self._get_next_statement()
            return BooleanStatement(data)            

    def _parse_import(self):
        if self.token == Token.IMPORT:
            self._is_next_token(Token.SYMBOL)
            if self.token.value != "=" and self.token.value != ":":
                self.raise_error(f"expected \":\" or \"=\" found {self.token.value}", exception="SyntaxError")
            arr = []
            while self._is_next_token(Token.STRING):
                arr.append(self.token)
                self._get_next_statement()
                if self.token != Token.SYMBOL:
                    break
                if self.token.value != ",":
                    self.raise_error(f"expected \",\" found \"{self.token.value}\"", exception="SyntaxError") 
            return ImportStatement(arr)

    def _parse_assignment(self):
        if self.token == Token.IDENTIFIER:
            variable_name = self.token
            self._is_next_token(Token.SYMBOL)
            if self.token.value == "=" or  self.token.value == ":":
                self._get_next_statement()
                return AssignmentStatment(variable_name,  self.next_expression(), is_global=self.token.value == ":")
            else:
                self.raise_error(f"expected \":\" or \"=\" found {self.token.value}")

        elif self.token == Token.D_IDENTIFIER:
            variable_name = self.token
            self._get_next_statement()
            return DAssignmentStatement(variable_name)
            


    def __next__(self): return self.next_expression()

    def __iter__(self): return self
