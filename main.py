from sys import argv, stderr
from lib.lexer import Lexer
from lib.parser import Parser
from lib.tokens import Token
from lib.environment import GlobalEnv
from argparse import ArgumentParser


parse = ArgumentParser()
cli_help = {'scenario_file': 'Scenario file name to execute.',
            'scenario_name': 'Execute single scenario with the given name.',
            'pcap_file': 'Pcap File name to execute'
            }

# setting up the arguments
parse.add_argument('--scn_file', help=cli_help['scenario_file'])
parse.add_argument('--scn_name', help=cli_help['scenario_name'])
parse.add_argument('--pcap_file', help=cli_help['pcap_file'])
parse.add_argument("-v", "--verbose", action="store_true")
args = parse.parse_args()

if not args.scn_file:
    print(parse.print_help())
    exit()


def Evaluator(lexer, parser, env):
    for parser in parser:
        print(parser)
        parser.eval(env, lexer)


def main():
    try:
        file_name = args.scn_file
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