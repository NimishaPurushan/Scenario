from logging import exception
from .syntax_tree import *
from .tokens import Token


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.token = None
        self._get_next_statement()

    def raise_error(self, message, *, exception="Exception"):
       self.lexer.raise_error(message, exception=exception)

    def next_expression(self):
        print(self.token)
        if self.token == Token.EOF:
            raise StopIteration()
        return (
            self._parse_values() or
            self._parse_assignment() or
            self._parse_import() or
            self._parse_scenario())

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
  
    def _parse_scenario(self):
        print(self.token == Token.SCENARIO_START)
        if self.token == Token.SCENARIO_START:
            self._get_next_statement()
            if self.token.value != ":":
                self.raise_error(f"expected \":\" found {self.token.value}", exception="SyntaxError")
            self._get_next_statement()
            test_name = self.token
            blocks_command = []
            self._get_next_statement()
            while self.token != Token.SCENARIO_END:
                print(blocks_command)
                if self.token == Token.EOF:
                    self.raise_error(f"unexpected \"EOF\" expected {Token.SCENARIO_END.value}", exception="SyntaxError")
                blocks_command.append(self.next_expression())
            return ScenarioStatement(test_name, blocks_command)

    def _parse_values(self):
        if self.token == Token.INTEGER:
            self._get_next_statement()
            return IntegerStatement(self.token)
        elif self.token == Token.STRING:
            self._get_next_statement()
            return StringStatement(self.token)
        elif self.token == Token.FALSE or self.token == Token.TRUE:
            self._get_next_statement()
            return BooleanStatement(self.token)            

    def _parse_import(self):
        if self.token == Token.IMPORT:
            variable_name = self.token
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

    def __next__(self): return self.next_expression()

    def __iter__(self): return self
