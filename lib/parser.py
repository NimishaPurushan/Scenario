from logging import exception
from logging.config import IDENTIFIER
from .logger import FrameworkLogger, ScenarioLogger
from .syntax_tree import *
from .tokens import Token, INFIX_OPERATION, INBUILT_FUNCTION_LIST

log = FrameworkLogger(__name__)
tc_log = ScenarioLogger(__name__)

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.token = None
        self._get_next_token()

    def next_expression(self):
        if self.token == Token.Eof:
            raise StopIteration()
        return (
            self._parse_number() 
            or self._parse_string()
            or self._parse_boolean()
            or self._parse_assignment() 
            or self._parse_import()
            or self._parse_scenario()
            or self._parse_if_else()
            or self._parse_function() 
            or self._parse_list()
            or self._parse_dict()
            or self._parse_unknown())

    def _get_next_token(self):
        # reads next token and retuns current token
        data  = self.token
        self.token = self.lexer.token
        return data

    def _parse_unknown(self):
        raise  SyntaxError(f"Unknown Token:{self.token}  data:\"{self.lexer.data}\" ord:{[x for x in self.lexer.data]}")
    
    def _parse_list(self):
        if self.token == Token.LBrace:
            data = []
            while self.token != Token.RBrace:
                self._get_next_token()
                data.append(self.next_expression())
                if not (self.token == Token.Comma or  self.token == Token.RBrace):
                    raise SyntaxError(f"expected \",\" or \"]\" found \"{self.lexer.data}\"")
            self._get_next_token()
            return ListStatement(data)
    
    def _parse_dict(self):
        if self.token == Token.LCurly:
            data = {}
            while self.token != Token.RCurly:
                self._get_next_token()
                key = self.next_expression()
                if self.token != Token.Colon :
                    raise SyntaxError(f"{self.token}expected \":\" found {self.lexer.data}")
                self._get_next_token()
                value = self.next_expression()
                if key in data:
                    raise SyntaxError(f"duplicate argument {key}")
                data[key] = value

            self._get_next_token()
            return DictStatement(data)

    def _parse_function(self):
        if self.token == Token.Function:
            function = INBUILT_FUNCTION_LIST[self.lexer.data]
            self._get_next_token()
            args = [] 
            pos = lambda: self.lexer.reader.line_no
            current_pos = pos()
            while pos() == current_pos and self.token != Token.Identifier:
                args.append( self.next_expression())

            kargs = {}
            while self.token == Token.Identifier:
                variable_name = StringStatement(self.lexer.data)
                self._get_next_token()
                if self.token == Token.Colon:
                    self._get_next_token()
                    if variable_name in kargs:
                        raise SyntaxError(f"duplicate argument {variable_name}")
                    kargs[variable_name] = self.next_expression()
                else:
                    raise SyntaxError(f"expected \":\" found \"{self.lexer.data}\"")
            return FunctionStatement(function, ListStatement(args), DictStatement(kargs))

    def _parse_if_else(self):
        if self.token == Token.If:
            self._get_next_token()
            condition = self.next_expression()
            blocks_command = [
                [], # true block
                []] # false block
            ptr = 0
            while self.token != Token.End:
                if self.token == Token.Else:
                    ptr+=1
                elif self.token == Token.Eof:
                    raise SyntaxError(f"unexpected \"EOF\" expected {Token.End}")
                blocks_command[ptr].append(self.next_expression())
            self._get_next_token()
            return IfStatement(condition, BlockStatement(blocks_command[False]), BlockStatement(blocks_command[True]))

    def _parse_scenario(self):
        if self.token == Token.Scenario:
            self._get_next_token()
            if self.token != Token.Identifier:
                raise SyntaxError(f"expected \"Identifier\" found \"{self.lexer.data}\"")
            self._get_next_token()
            test_name = self.token
            blocks_command = []
            while self.token != Token.End:
                if self.token == Token.Eof:
                    raise SyntaxError(f"unexpected \"EOF\" expected \"{Token.End}\"")
                blocks_command.append(self.next_expression())
            self._get_next_token()
            return ScenarioStatement(test_name, BlockStatement(blocks_command))

    def _parse_number(self):
        if self.token == Token.Integer:
            lhs =  IntegerStatement(self.lexer.data)
            self._get_next_token()
            return self._parse_infix_statement(lhs) or lhs

    def _parse_string(self):
        if self.token == Token.String:
            lhs = StringStatement(self.lexer.data)
            self._get_next_token()
            return self._parse_infix_statement(lhs) or lhs

    def _parse_infix_statement(self, lhs):
        if self._is_operator():
            operator = self.token
            self._get_next_token()
            rhs = self.next_expression()
            return InfixStatement(lhs, operator.value, rhs)

    def _parse_boolean(self):
        if self.token == Token.Falsy or self.token == Token.Truthy:
            lhs = BooleanStatement(self.lexer.data) 
            self._get_next_token()
            return self._parse_infix_statement(lhs) or lhs

    def _parse_import(self):
        if self.token == Token.Import:
            arr = []
            self._get_next_token()
            while self.token == Token.String:
                arr.append(self.lexer.data)
                self._get_next_token()

            if len(arr) == 0:
                raise SyntaxError(f"expected importpath found \"{self.token}\"") 
            if self.token != Token.End:
                raise SyntaxError(f"expected \"END\" found \"{self.token}\"") 
            self._get_next_token()
            return ImportStatement(arr)

    def _parse_assignment(self):
        if self.token == Token.DIdentifier:
            lhs = self.lexer.data
            self._get_next_token()
            if self.token == Token.Assignment :
                self._get_next_token()
                return AssignmentStatment(lhs,  self.next_expression())
            return self._parse_infix_statement(lhs) or DAssignmentStatement(lhs)

  
    def __next__(self): return self.next_expression()

    def __iter__(self): return self
   
    def _is_operator(self):
        return  self.token.value in INFIX_OPERATION
