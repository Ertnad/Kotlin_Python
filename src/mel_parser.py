from contextlib import suppress
import inspect

import pyparsing as pp
from pyparsing import pyparsing_common as ppc

from mel_ast import *


def _make_parser():
    LPAR, RPAR = pp.Literal('(').suppress(), pp.Literal(')').suppress()
    LBRACE, RBRACE = pp.Literal('{').suppress(), pp.Literal('}').suppress()
    COMMA, SEMI = pp.Literal(',').suppress(), pp.Literal(';').suppress()
    ASSIGN = pp.Literal('=')
    MULT, ADD = pp.oneOf(('* /')), pp.oneOf(('+ -'))

    # INPUT = pp.Keyword('input')
    # OUTPUT = pp.Keyword('output')
    IF = pp.Keyword('if')
    ELSE = pp.Keyword('else')
    FOR = pp.Keyword('for')

    keywords = IF | ELSE | FOR

    num = ppc.fnumber.copy().setName('')
    ident = ~keywords + ppc.identifier  # ~ переопределён для парсера и означает не keywords

    expr = pp.Forward()
    ''' (expr (',' expr)*)? '''

    params = pp.Optional(expr + pp.ZeroOrMore(COMMA + expr))
    call = ident + LPAR + params + RPAR
    group = call | ident | num | LPAR + expr + RPAR
    mult = group + pp.ZeroOrMore(MULT + group)
    add = mult + pp.ZeroOrMore(ADD + mult)

    expr << add

    stmt = pp.Forward()
    stmt_or_empty = stmt | pp.Group(pp.empty).setName("stmt_list")
    # stmt_or_empty = stmt | pp.empty.copy().setName("stmt_list")

    #input = INPUT.suppress() + ident
    #output = OUTPUT.suppress() + expr
    assign = ident + ASSIGN.suppress() + expr

    if_ = pp.Keyword("if").suppress() + LPAR + expr + RPAR + stmt + \
        pp.Optional(pp.Keyword("else").suppress() + stmt)

    # условие(expr) не empty
    for_ = FOR.suppress() + LPAR + stmt_or_empty + SEMI + expr + SEMI + stmt_or_empty + stmt

    stmt_list = pp.Forward()  # объявляем
    stmt << (
            call |
            assign |
            if_ |
            LBRACE + stmt_list + RBRACE
    )
    stmt_list << pp.ZeroOrMore(stmt)  # переопределяем
    program = stmt_list.ignore(pp.cStyleComment).ignore(pp.dblSlashComment) + pp.StringEnd()

    start = program

    def set_parse_action_magic(rule_name: str, parser: pp.ParserElement)->None:
        if rule_name == rule_name.upper():
            return
        if getattr(parser, 'name', None) and parser.name.isidentifier():
            rule_name = parser.name
        """
            temp = getattr(parser, 'name', None)
        print(temp)
        if isinstance(temp, str) and temp.isidentifier():
            rule_name = temp
        #rule_name = getattr(parser, 'name', None)
        print(rule_name)
        """
        if rule_name in ('mult', 'add'):
            def bin_op_parse_action(s, loc, tocs):
                node = tocs[0]
                for i in range(1, len(tocs) - 1, 2):
                    node = BinOpNode(BinOp(tocs[i]), node, tocs[i + 1])
                return node
            parser.setParseAction(bin_op_parse_action)
        else:
            cls = ''.join(x.capitalize() for x in rule_name.split('_')) + 'Node'
            with suppress(NameError):
                cls = eval(cls)
                if not inspect.isabstract(cls):
                    def parse_action(s, loc, tocs):
                        return cls(*tocs)

                    parser.setParseAction(parse_action)

    for var_name, value in locals().copy().items():
        if isinstance(value, pp.ParserElement):
            set_parse_action_magic(var_name, value)

    return start


parser = _make_parser()


def parse(prog: str)->StmtListNode:
    return parser.parseString(str(prog))[0]
