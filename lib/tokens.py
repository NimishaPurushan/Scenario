from enum import Enum
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
    ELse       = 62
    Scenario   = 63
    Import     = 64
    End        = 65
    # operator
    Plus       = 51
    Minus      = 52
    Multiply   = 53
    Divide     = 54

    IDENTIFIER   = 3   # assignment 
    D_IDENTIFIER = 4  # read only
    Function     = 8
   
    def __eq__(self, val): return self.value == val

# this is look up table for single char
LOOKUP_TABLE = {
    b''  : Token.Eof,
    b'[' : Token.LBrace,
    b']' : Token.RBrace,
    b':' : Token.Colon,
    b'{' : Token.LCurly,
    b'}' : Token.RCurly,
}

KEYWORD_TABLE = {
    b'TRUE'  : Token.Truthy,
    b'FALSE' : Token.Falsy,
    b'NONE'  : Token.Nil,
    b'IF'    : Token.If,
    b'ELSE'  : Token.ELse,
    b'END'   : Token.End,
    b'SCENARIO'   : Token.Scenario
}

INBUILT_FUNCTION_LIST = {
    "PACKET_FILTER"    : PcapAnalyser().tshark_validate,
    "CHECK_TIMING_INFO":  PcapAnalyser().check_timing,
    "SET_TSHARK_PATH"  : PcapAnalyser.set_tshark_patch,
    "SHOW_PRINT"       : BaseLogger.set_display,
    "PRINT"            : print,
}

OPERATOR_TABLE = {
    b'+' : Token.Plus,
    b'-' : Token.Minus,
    b'*' : Token.Multiply,
    b'/' : Token.Divide,
    b'=' : Token.Assignment,
    b'==': Token.Eq,
    b'!' : Token.Not,
    b'!=': Token.Ne,
    b'>' : Token.Gt,
    b'<' : Token.Lt,
    b'>=': Token.Gte,
    b'<=': Token.Lte,
}