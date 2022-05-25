from logging import exception
from sre_parse import GLOBAL_FLAGS
from .syntax_tree import *
from .tokens import Token
from ast import *


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.token = None
        self._get_next_statement()

    def _get_next_statement(self):
        data = self.token
        self.token = next(self.lexer)
        return data

    def next_expression(self):
        if self.token == Token.EOF:
            raise StopIteration()
        
        return (
            self._parse_values() or
            self._parse_assignment())

    def _is_next_token(self, expected_token=None, expected_value=None):
        self._get_next_statement()
        if expected_token == None or self.token != expected_token:
            self.lexer.raise_error(f"expected {expected_token} found {self.token}", exception="TypeError")
                   
        if (expected_value == None and expected_value == self.token.value ):
            self.lexer.raise_error(f"expected {expected_value} found {self.token.value}",  exception="ValueError")
        return True

    def _parse_values(self):
        if self.token == Token.INTEGER:
            return IntegerStatement(self.token)
        elif self.token == Token.STRING:
            return StringStatement(self.token)
        elif self.token == Token.FALSE or self.token == Token.TRUE:
            return BooleanStatement(self.token)

    def _parse_assignment(self):
        if self.token == Token.IDENTIFIER:
            variable_name = self.token
            if self._is_next_token(Token.SYMBOL):
                if self.token.value == "=" or  self.token.value == ":":
                    self._get_next_statement()
                    return AssignmentStatment(variable_name,  self.next_expression(), is_global=self.token.value == ":")
                else:
                    self.lexer.raise_error(f"expected \":\" or \"=\" found {self.token.value}")

    def __next__(self): return self.next_expression()

    def __iter__(self): return self


