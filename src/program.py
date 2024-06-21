import sys
import traceback
import os

from src import semantic_base, mel_parser
from src import semantic_checker
from src import msil


def execute(prog: str, msil_only: bool = False, file_name: str = None) -> None:
    try:
        prog = mel_parser.parse(prog)
    except Exception as e:
        print('Ошибка: {}'.format(e.message), file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        exit(1)

    if not msil_only:
        print('ast:')
        print(*prog.tree, sep=os.linesep)

    if not msil_only:
        print()
        print('semantic-check:')
    try:
        checker = semantic_checker.SemanticChecker()
        scope = semantic_checker.prepare_global_scope()
        checker.semantic_check(prog, scope)
        if not msil_only:
            print(*prog.tree, sep=os.linesep)
            print()
    except semantic_base.SemanticException as e:
        print('Ошибка: {}'.format(e.message), file=sys.stderr)
        exit(2)

    print()
    print('msil:')
    try:
        gen = msil.MsilCodeGenerator()
        gen.gen_program(prog)
        print(*gen.code, sep=os.linesep)
    except msil.MsilException or Exception as e:
        print('Ошибка: {}'.format(e.message), file=sys.stderr)
        exit(3)
