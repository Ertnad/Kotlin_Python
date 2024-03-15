import os
import mel_parser


def main():
    prog = '''
        a = input() b = input()  /* comment 1
        c = input()
        */
        c = a + b * (2 - 1) + 0  // comment 2
        pirnt(c + sin(5))

        if ( a + 7 ) { b = 9 b = b + 1}
    '''
    prog2 = '''
        if (a) print()
    '''
    prog = mel_parser.parse(prog)
    print(*prog.tree, sep=os.linesep)


if __name__ == "__main__":
    main()
