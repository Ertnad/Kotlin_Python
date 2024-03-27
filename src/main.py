import os
import mel_parser


def main():
    prog1 = '''
            if (a) {
                print(1 + 2);
                print(0);
                if (b) {
                    b = 1;
                }
            } else if (b) {
                print(4);
            } else if (c) {
                c = b + c;
            } else {
                print(c);
            }
        '''
    prog2 = """
        a = 5;
        b = !!a;
    """
    prog3 = """
        a = 10;
        b = 20;
        when{
            (a < 90)->{
                print(a)
                a = 2
            }
            in 40 ..10->print(b)
        }
    """
    prog4 = """
            a = 10;
            b = 20;
            when(a){
                (a < 90)->{
                    print(a)
                    a = 2
                }
                in 10 .. 30->print(b)
            }
        """
    prog5 = """
        val a: Int = 1
    """
    prog6 = """
            for(i = 8; i < 9; i = i + 1) {
                print(i)
            }
        """
    prog7 = """
                for(; i < 9;) {
                    print(i)
                    i = i + 1
                }
            """
    prog = mel_parser.parse(prog7)
    print(*prog.tree, sep=os.linesep)


if __name__ == "__main__":
    main()