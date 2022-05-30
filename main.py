from sys import argv, stderr
from argparse import ArgumentParser
import traceback

from lib.logger import FrameworkLogger, ScenarioLogger

log = FrameworkLogger(__name__)
sc_log = ScenarioLogger(__name__)


parse = ArgumentParser()
cli_help = {
    'scenario_file': 'Scenario file name to execute.',
    'scenario_name': 'Execute single scenario with the given name.',
    'pcap_file'    : 'Pcap File name to execute'
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


def Evaluator(ast_list, env):
    for p in ast_list:
        p.eval(env)



def main(file_name=args.scn_file):
    from lib.lexer import Lexer
    from lib.parser import Parser
    from lib.environment import GlobalEnv
    from lib.file_reader import FileReader
    
    reader = FileReader(file_name)
    global_env = GlobalEnv(reader)
    try:
        lexer = Lexer(reader)
        parser = Parser(lexer)
        ast_list = []
        for p in parser:
            if hasattr(p, "immediately_execute"):
                p.eval(global_env)
            else:
                ast_list.append(p)
        Evaluator(ast_list, env=global_env)
    except Exception as E:
        reader.read_line()
        sc_log.console_error(f"---------------------------------")
        sc_log.console_error(f"File \"{file_name}\", in line {reader.line_no}, pos {reader.pos}")
        sc_log.console_error(reader.line.decode().strip())
        sc_log.console_error(" "*(reader.pos-1) + "^")
        sc_log.console_error(f"{type(E).__name__}: {E}")
        sc_log.console_error("---------------------------------")

        global_env.traceback()
        traceback.print_exc()
if __name__ == "__main__":
    main()
