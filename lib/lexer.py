from lib2to3.pgen2.token import LBRACE
from .tokens import *
from .utils import file_next_iterator
from .logger import FrameworkLogger, ScenarioLogger

log = FrameworkLogger(__name__)
sc_log = ScenarioLogger(__name__)


__all__ = ("Lexer",)



class Lexer:
    
    __slots__ = ("reader", "ch", "_byte_data", "_exception")
    
    def __init__(self, reader):
        self.reader = reader
        self.ch = b''
        self._get_next_char()
        self._byte_data = bytearray() # temporary buffer of data
  
    @property
    def data(self) -> str:
        return self._byte_data.decode()
    
    @property
    def token(self) -> Token:
        """ returns next token """
        return (
            # preprocessing
            self._remove_white_space()  
            or self._remove_comment()      
            or self._get_easy_tokens()    
            # returning value
            or self._get_number_token()   
            or self._get_string_token()    
            or self._get_operator_token()  
            or self._get_identfier_token() 
            or self._get_variable_token()  
            or self._get_eol())

    def _get_eol(self):
        if self._is_eof():
            return Token.Eof

    def _get_easy_tokens(self) -> None:
        # these are one charector tokens that dont
        # need extra processing
        if self.ch in LOOKUP_TABLE:
            token = LOOKUP_TABLE[self.ch]
            self._get_next_char()
            return token

    def _get_next_char(self):
        self.ch = self.reader.ch

    def _remove_white_space(self) -> None:
        while self._is_whitespace():
            self._get_next_char()
    
    def _remove_comment(self) -> None:
        if self._is_comment():
            while not self._is_newline():
                self._get_next_char()
            return self.token

    def _get_number_token(self) -> Token:
        """ the language has int and float types."""
        if self._is_number():
            self._byte_data = bytearray()
            while self._is_number():
                self._byte_data.extend(self.ch)
                self._get_next_char()
            self._get_next_char()
            return Token.Integer
            
    def _get_string_token(self) -> Token:
        """ string sart with either " or '. 
        all strings are multiline """
        if self.ch == b'\"':
            self._byte_data = bytearray()
            self._get_next_char()
            while self.ch != b'\"':
                self._byte_data.extend(self.ch)
                self._get_next_char()
            self._get_next_char()
            return Token.String

        elif self.ch == b'\'':
            self._byte_data = bytearray()
            self._get_next_char()
            while self.ch != b'\'':
                self._byte_data.extend(self.ch)
                self._get_next_char()
                
            self._get_next_char()
            return Token.String

    def _get_identfier_token(self) -> Token:
        if self._is_identifier():
            self._byte_data = bytearray()
            while self._is_identifier() or self._is_number():
                self._byte_data.extend(self.ch)
                self._get_next_char()
            if self.data in KEYWORD_TABLE:
                return KEYWORD_TABLE[self.data]
            elif self._is_function():
                return Token.Function
            else:
                return Token.Identifier
        
    def _get_variable_token(self) -> Token:
        if self.ch == b'$':
            self._get_next_char()
            if self.ch != b'{':
                raise SyntaxError("expected '{' found '%s'" % self.ch)
            self._get_next_char()
            self._byte_data = bytearray()
            while self._is_identifier() or self._is_number():
                self._byte_data.extend(self.ch)
                self._get_next_char()
            if self.ch != b'}':
                raise SyntaxError("expected '}' found '%s'" % self.ch)
            self._get_next_char()
            return Token.DIdentifier

    def _get_operator_token(self) -> Token:
        """ multi symbols like """
        if self._is_operator():
            self._byte_data = bytearray()
            key = self.ch
            self._get_next_char()
            if self.ch == b'=':
                self._byte_data.extend(self.ch)
                self._get_next_char()
                return OPERATOR_TABLE[self.data]
            return OPERATOR_TABLE[key]

    def _is_newline(self) -> Token:
        return self.ch == b'\n' or self.ch == b'\t'

    # predicate functions
    def _is_operator(self):
        return (
            self.ch == b'+' or self.ch == b'-' 
            or self.ch == b'*' or self.ch == b'/' 
            or self.ch == b'=' or self.ch == b'>'
            or self.ch == b'<')

    def _is_whitespace(self) -> bool:
        return (
            self.ch == b'\n' or self.ch == b'\r' 
            or self.ch == b' ' or self.ch == b'\t')

    def _is_comment(self) -> bool:
        return self.ch == b'#'

    def _is_eof(self) -> bool:
        return self.ch == b'' or len(self.ch) == 0

    def _is_number(self) -> bool:
        return (
            b'0' <= self.ch <= b'9' 
            or self.ch == b'.')

    def _is_identifier(self) -> bool:
        return (
            b'a' <= self.ch <= b'z' 
            or b'A' <= self.ch <= b'Z' 
            or b'_' == self.ch)

    def _is_function(self) -> bool:
        return self.data in INBUILT_FUNCTION_LIST

    # making Lexer class iterable
    def __next__(self): return self.token

    def __iter__(self): return self
