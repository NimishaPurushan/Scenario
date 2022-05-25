from sys import argv, stderr
from lib.lexer import Lexer
from lib.parser import Parser
from lib.tokens import Token
from lib.environment import GlobalEnv


def Evaluator(lexer, parser, env):
    for parser in parser:
        print(parser)
        parser.eval(env, lexer)


def main():
    try:
        file_name = argv[1]
    except IndexError:
        raise AssertionError("input File as: python main.py <file_name>")
    try:
        global_env = GlobalEnv(file_name)
        lexer = Lexer(file_name)
        parser = Parser(lexer)
        Evaluator(lexer, parser, env=global_env)
    except AssertionError:
        global_env.traceback()
    except Exception as E:
        import traceback
        print(E, file=stderr)
        traceback.print_exc()
    

if __name__ == "__main__":
    main()