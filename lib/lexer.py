from sys import stderr
import traceback
from .tokens import Token, TokenInfo, is_function
from .utils import file_next_iterator


class Lexer:
    def __init__(self, file_name):
        self.file_name = file_name
        self.lineno = 0 # for showing error message
        # string are immutable. It is an expensive to slice string unnecessarity.
        # so just read the postion of string accordingly 
        self.pos = 0  # points to next position in line
        self.line = ""
        self.char = "" # current char
        self.file_iter = file_next_iterator(self.file_name)
        self.__get_next_line()

    def next_token(self) -> TokenInfo:
        """ returns next token """
        try:
            return (self._remove_white_space() or
                self._get_number_token() or
                self._get_string_token() or
                self._get_identfier_token() or
                self._get_symbol_token())
        except StopIteration:
            return TokenInfo(Token.EOF, None)

    def raise_error(self, message, *, exception="Exception"):
        print("---------------------------------", file=stderr)
        print(f"File \"{self.file_name}\", in line {self.lineno}", file=stderr)
        print(self.line, file=stderr)
        print(f"{exception}: {message}", file=stderr)
        print("---------------------------------", file=stderr)
        assert False

    def _get_next_char(self):
        """ reads the current postion of string while updating position """
        if self.pos >= len(self.line):
            self.__get_next_line()
        data = self.char
        self.char = self.line[self.pos]
        self.pos += 1
        return data

    def __get_next_line(self):
        self.lineno, self.line = next(self.file_iter)
        self.pos = 0
   
    def _remove_white_space(self):
        while self.__is_whitespace(): 
            self._get_next_char()

    def _get_number_token(self):
        """ the language has int and float types."""
        if self.__is_number():
            _start = self.pos
            while self.__is_number():
                self._get_next_char()
            data = self.line[_start-1: self.pos-1]
            return TokenInfo(Token.INTEGER, data) 
            
    def _get_string_token(self):
        """ string sart with either " or '. 
        There is no multi line string """
        for ch in ["\"", "\'"]:
            if self.char == ch:
                _start = self.pos
                self._get_next_char()
                while self.char != ch:
                    self._get_next_char()
                    if self.__is_newline():
                        self.raise_error(f"expected {ch} found newline")

                data = self.line[_start: self.pos-1]
                self._get_next_char()
                return TokenInfo(Token.STRING, data)

    def _get_keyword_token(self, data):
        """ checks if identifier is string """
        if data == Token.IF_START:
            return TokenInfo(Token.IF_START, None)
        elif data == Token.IF_END:
            return TokenInfo(Token.IF_END, None)
        elif data == Token.SENARIO_START:
            return TokenInfo(Token.SENARIO_START, None)
        elif data == Token.SENARIO_END:
            return TokenInfo(Token.SENARIO_END, None)
        elif data == Token.IF_ELSE:
            return TokenInfo(Token.IF_ELSE, None)
        elif data == Token.FALSE:
            return TokenInfo(Token.FALSE, None)    
        elif data == Token.TRUE:
            return TokenInfo(Token.FALSE, None)
        elif is_function(data):
            return TokenInfo(Token.INBUILT_FUNCTION, None)    
        else:
            return TokenInfo(Token.IDENTIFIER, data)
     
    def _get_identfier_token(self):
        """ string also can exist without quotes. 
        But it starts but must starts with underscore or string.
        ${} symbol is for reading variable"""
        if self.__is_identifier():
            _start = self.pos
            while self.__is_identifier() or self.__is_number():
                self._get_next_char()
            data = self.line[_start-1: self.pos-1]
            return self._get_keyword_token(data)
        
        if self.char == "$":
            if self.__is_next_char("{"):
                self.raise_error("expected '{' found '%s'" % self.char)
            _start = self.pos
            while self.char != "}":
                self._get_next_char()
                if self.__is_newline():
                    self.raise_error("variable access not terminated by '}'")
            data = self.line[_start-1: self.pos-1]
            return TokenInfo(Token.D_IDENTIFIER, data)

    def _get_symbol_token(self):
        """ multi symbols like """
        if self.__is_symbol():
            data = self._get_next_char()
            if self.__is_next_char("="):
                self._get_next_char()
                return TokenInfo(Token.SYMBOL, self.line[self.pos-1:self.pos])
            else:
                return TokenInfo(Token.SYMBOL, data)
        elif self.__is_bracket():
            data = self._get_next_char()
            return TokenInfo(Token.BRACKET, data)
        elif self.char == ":" or self.char == ",":
            data = self._get_next_char()
            return TokenInfo(Token.SYMBOL, data)
    
    def __is_newline(self):
        return (self.char == "\n" or self.char == "\t")

    def __is_bracket(self):
        return (self.char == "{" or self.char == "}" or
            self.char == "[" or self.char == "]" or
            self.char == "(" or self.char == ")")

    def __is_next_char(self, ch: str) -> bool:
        """ reads if the next postion only if it is expected value"""
        return ( len(self.line) <= self.pos + 1 or 
            self.line[self.pos + 1] == ch)

    def __is_symbol(self):
        return(self.char == "+" or self.char == "-" or
            self.char == "*" or self.char == "/" or
            self.char == "=")

    def __is_whitespace(self) -> bool:
        return (self.char == "\n" or self.char == "\r" or
                self.char == " " or self.char == "\t" or
                self.char == "")

    def __is_number(self) -> bool:
        return ("0" <= self.char <= "9" or
                self.char == ".")

    def __is_identifier(self) -> bool:
        return ("a" <= self.char <= "z" or 
                "A" <= self.char <= "Z" or
                "_" <= self.char)

    # making Lexer class iterable
    def __next__(self): return self.next_token()

    def __iter__(self): return self
