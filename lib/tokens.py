from enum import Enum
from typing import Any, NamedTuple


class Token(Enum):
    EOF = -1
    STRING = 1
    IDENTIFIER = 3   # assignment 
    D_IDENTIFIER = 4  # read only
    SYMBOL = 5
    BRACKET = 6
    IF_START = "IF_START"
    ELSE = "ELSE"
    IF_END = "IF_END"
    SCENARIO_START ="SCENARIO_START"
    SCENARIO_END = "SCENARIO_END"
    NONE = "NONE"
    FALSE = "FALSE"
    TRUE = "TRUE"
    INTEGER = 13
    INBUILT_FUNCTION = 14
    IMPORT = "IMPORT"

    def __eq__(self, val):
        return self.value == val


INBUILT_FUNCTION_LIST = {
    "PACKET_FILTER": lambda **x: print("PACKET_FILTER", x),
    "CHECK_TIMING":  lambda **x: print("CHECK_TIMING", x)
}


def is_function(name):
    return name in INBUILT_FUNCTION_LIST


class TokenInfo(NamedTuple):
    token: Token
    value: Any

    def __repr__(self):
        return f"{self.token.name}(\"{self.value}\")"

    def __eq__(self, val):
        return val.value == self.token.value if isinstance(val, Token) else val == self

    def __ne__(self, val):
        return val.value != self.token.value if isinstance(val, Token) else val != self
