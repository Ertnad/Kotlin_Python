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
                in 10..30->print(b)
            }
        """
    prog5 = """
        val a: Int = 1
    """
    prog15 = """
        var a: Int = 1
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
    prog8 = """
            a = 5 + 6
            a = 5 - 6
            a = 5 * 6
            a = 5 / 6
            a = 5 >= 6
            a = 5 <= 6
            a = 5 > 6
            a = 5 < 6
            a = 5 == 6
            a = 5 != 6
            a = 5 && 6
            a = 5 || 6
            a = !!a
        """
    prog10 = """
        when(a + b){
            a -> println(b)
            b -> println(a)
            a + 5 -> println(a + 5)
            in 10..12 -> { a = a + 1 }
            !in 10..12 -> { isEnable = 2 }
            else -> { a = 3 }
        }
    """
    prog11 = """
        if (a > 3) {
            print(1);
            a = 3;
        }
    """
    prog12 = """
        c = when(a) {
            1 -> a
            2 -> a + 1
            else -> a + 1
        }
    """
    prog13 = """
        when{
            (b > 10) -> println(b)
            (a > 10) -> println(a)
            else -> println(c)
        }
    """
    prog14 = """
        c = if (a > b) a else if (a == b) b else d
    """
    prog16 = """
        fun sum():Int {
            for(i = 8; i < 9; i = i + 1) {
                print(i)
            }
        }
        """
    prog17 = """
    fun sum(a: int, b: int) : int {
        var result: int = 0
        for(i = 0; i < a; i = i + 1) {
            result = result + b
        }
        return result
    }
    """
    while_check = """
        var a: Int = 1
        while (a < 1) {
            print(a)
            a = a + 1
    }
    """
    for_each_check = """
        each(x in range(5)) {
            print(x);
        }
    """

    prog = mel_parser.parse(while_check)
    print(*prog.tree, sep=os.linesep)


if __name__ == "__main__":
    main()