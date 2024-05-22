import os
import sys
import traceback

import mel_parser
from src import semantic_checker, semantic_base
from src.semantic_checker import SemanticChecker


def main():
    prog1 = '''
        val a : Int = 2
            if (a == 2) {
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
        val a: Int = 1;
        var a: Int = 1;
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
        fun sum(a: Int, b: Int): Int{
            print(i);
            print(b);
            return a;
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
    prog18 = """
        val x: int = 2;
    while (x > 0) {
        if (x == 5) {
            x = x - 1;
            continue;
        }
        if (x < 3) {
            break;
        }
        x = x - 1;
    }
    """
    prog19 = """
        for (x in range(5)) {
            print(x);
        }
    """
    prog20 = """
        fun combinedFunction() {
            var a: int = 2;
            val b: int = 3 + 6;
            var c: int = 4;
            
            if (a) {
                b = !!a;
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
        }
        
        fun combinedFunction2() {
            val x: int = 2;
            while (x > 0) {
                if (x == 5) {
                    x = x - 1;
                }
                x = x - 1;
            }
            
            for (x in range(5)) {
                print(x);
            }
        }
        
        fun sum(a: int, b: int) : int {
            when{
                (b > 10) -> println(b)
                (a > 10) -> println(a)
                else -> println(c)
            }
            
            when(a + b){
                a -> {
                    println(b);
                    print(a);
                }
                b -> println(a)
                a + 5 -> println(a + 5)
                else -> { a = 3 }
            }
            
            when(a - b) {
                in 10..12 -> { a = a + 1 }
                !in 10..12 -> { isEnable = 2 }
            }
        }
        
        fun myFun(a: int) {
            c = if (a > b) a else if (a == b) b else d
        }
    """
    prog23 = """
        fun sum(a: int, b: int) : int {
            when(a + b){
                a -> println(b)
                b -> println(a)
                a + 5 -> println(a + 5)
                in 10..12 -> { a = a + 1 }
                !in 10..12 -> { isEnable = 2 }
                else -> { a = 3 }
            }
        }
        fun test() {
            a = 4
        }
    """
    prog21 = """
        fun sum(a: Int) {
            if (a > 3) {
                print(1);
                a = 3;
            }
        }
    """
    #var c = a + b + 2.3;
    prog22 = """
    fun sum(a: Float, b: Float) {
        a = 2.3;
    }
    fun printMyString(name: String) {
        print(name);
    }
    """
    prog23 = """
        fun sum(a: Int) {
            if (a > 3) {}
        }
        fun input_int(name: String) {
                c = if (a > b) a else if (a == b) b else d
            }
        """
    try:
        prog = mel_parser.parse(prog5)
    except Exception as e:
        print('Ошибка: {}'.format(e.message), file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        exit(1)
    print(*prog.tree, sep=os.linesep)
    print()
    print('semantic-check:')
    try:
        checker = SemanticChecker()
        scope = semantic_checker.prepare_global_scope()
        # prog.semantic_check(scope)
        checker.semantic_check(prog, scope)

        print(*prog.tree, sep=os.linesep)
        print()
    except semantic_base.SemanticException as e:
        print('Ошибка: {}'.format(e.message), file=sys.stderr)
        exit(2)


if __name__ == "__main__":
    main()
