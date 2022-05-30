from enum import Enum

from numpy import multiply
from .inbuilt_functions import PcapAnalyser
from .logger import BaseLogger

class Token(Enum):
    Eof     = -1
    Unknown = 0
    # datatypes
    String  =  10    
    Integer =  11
    Float   =  12
    Truthy  =  13
    Falsy   =  14
    Nil     =  15
    # brackets
    LBrace  =  21
    RBrace  =  22
    LCurly  =  23
    RCurly  =  24
    # delimiter
    Colon   =  31
    Comma   =  32
    # logical operator
    Assignment = 41
    Eq         = 42
    Not        = 43
    Ne         = 44
    Gt         = 45
    Lt         = 46
    Gte        = 47
    Lte        = 48
    # Keyword
    If         = 61
    Else       = 62
    Scenario   = 63
    Import     = 64
    End        = 65
    # operator
    Plus       = 51
    Minus      = 52
    Multiply   = 53
    Divide     = 54

    Identifier   = 3   # assignment 
    DIdentifier  = 4  # read only
    Function     = 8
    RSlash       = 9
   
    def __eq__(self, val): return self.value == val

# this is look up table for single char
LOOKUP_TABLE = {
    b''  : Token.Eof,
    b'[' : Token.LBrace,
    b']' : Token.RBrace,
    b':' : Token.Colon,
    b'{' : Token.LCurly,
    b'}' : Token.RCurly,
    b'\\' : Token.RSlash,
    b',' : Token.Comma
}

KEYWORD_TABLE = {
    'TRUE'       : Token.Truthy,
    'FALSE'      : Token.Falsy,
    'NONE'       : Token.Nil,
    'IF'         : Token.If,
    'ELSE'       : Token.Else,
    'END'        : Token.End,
    'SCENARIO'   : Token.Scenario,
    'IMPORT'     : Token.Import,
}

INBUILT_FUNCTION_LIST = {
    "PACKET_FILTER"    : PcapAnalyser().tshark_validate,
    "CHECK_TIMING_INFO":  PcapAnalyser().check_timing,
    "SET_TSHARK_PATH"  : PcapAnalyser.set_tshark_patch,
    "SET_PRINT"       : BaseLogger.set_display,
    "PRINT"            : print
}

OPERATOR_TABLE = {
    b'+' : Token.Plus,
    b'-' : Token.Minus,
    b'*' : Token.Multiply,
    b'/' : Token.Divide,
    b'=' : Token.Assignment,
    '==': Token.Eq,
    b'!' : Token.Not,
    '!=': Token.Ne,
    b'>' : Token.Gt,
    b'<' : Token.Lt,
    '>=': Token.Gte,
    '<=': Token.Lte,
}

INFIX_OPERATION = {
    Token.Plus.value:      lambda x,y:  x + y,
    Token.Minus.value:     lambda x,y:  x - y,
    Token.Divide.value:    lambda x,y:  x / y,
    Token.Multiply.value:  lambda x,y:  x * y,
    Token.Lt.value:  lambda x,y:  x < y,
    Token.Gt.value:  lambda x,y:  x > y,
    Token.Eq.value:  lambda x,y:  x == y,
    Token.Ne.value:  lambda x,y:  x != y,
    Token.Gte.value: lambda x,y:  x >= y,  
    Token.Lte.value: lambda x,y:  x <= y,  
}

