from contextlib import suppress
import inspect

import pyparsing as pp
from pyparsing import pyparsing_common as ppc

from mel_ast import *


def _make_parser():
    LPAR, RPAR = pp.Literal('(').suppress(), pp.Literal(')').suppress()
    LBRACE, RBRACE = pp.Literal('{').suppress(), pp.Literal('}').suppress()
    COMMA, SEMI, POINT = pp.Literal(',').suppress(), pp.Literal(';').suppress(), pp.Literal('.').suppress()
    ASSIGN = pp.Literal('=')
    MULT, DIV, MOD = pp.Literal('*'), pp.Literal('/'), pp.Literal('%')
    PLUS, MINUS = pp.Literal('+'), pp.Literal('-')

    GE, LE, GT, LT = pp.Literal('>='), pp.Literal('<='), pp.Literal('>'), pp.Literal('<')
    EQUALS, NOTEQUALS = pp.Literal('=='), pp.Literal('!=')
    LOGIC_AND, LOGIC_OR = pp.Literal('&&'), pp.Literal('||')
    NOT = pp.Literal('!')
    OPERATOR = pp.Literal('->').suppress()
    COLON = pp.Literal(':').suppress()

    IF = pp.Keyword('if').suppress()
    ELSE = pp.Keyword('else').suppress()
    WHILE = pp.Keyword('while').suppress()
    WHEN = pp.Keyword('when').suppress()
    FOR = pp.Keyword('for').suppress()
    IN = pp.Keyword('in').suppress()

    VAL = pp.Keyword('val')
    VAR = pp.Keyword("var")
    FUN = pp.Keyword("fun")

    keywords = IF | ELSE | WHILE | WHEN | FOR | IN | VAL | VAR | FUN

    num = ppc.fnumber.copy().setName('num')
    ident = ~keywords + ppc.identifier  # ~ переопределён для парсера и означает не keywords
    type_ = ident.copy().setName('type')

    expr = pp.Forward()
    params = pp.Optional(expr + pp.ZeroOrMore(COMMA + expr))
    call = ident + LPAR + params + RPAR
    group = call | ident | num | LPAR + expr + RPAR
    not_ = pp.Forward().setName('unary')
    not_ << (NOT + (not_ | group))
    not_or_group = not_ | group
    mult = (not_or_group + pp.ZeroOrMore((MULT | DIV | MOD) + not_or_group)).setName('binary')
    add = (mult + pp.ZeroOrMore((PLUS | MINUS) + mult)).setName('binary')
    compare = (add + pp.Optional((GE | LE | GT | LT | EQUALS | NOTEQUALS) + add)).setName('binary')
    logic_and = (compare + pp.ZeroOrMore(LOGIC_AND + compare)).setName('binary')
    logic_or = (logic_and + pp.ZeroOrMore(LOGIC_OR + logic_and)).setName('binary')

    expr << logic_or

    stmt = pp.Forward()
    empty_stmt = pp.Group(pp.empty).setName("stmt_list")
    stmt_or_empty = stmt | empty_stmt

    empty_expr = pp.Group(pp.empty).setParseAction(lambda s, loc, tocs: NumNode(1))
    expr_or_empty = expr | empty_expr

    assign = ident + ASSIGN.suppress() + expr

    if_ = IF + LPAR + expr + RPAR + stmt + pp.Optional(ELSE + stmt)

    for_ = FOR + LPAR + stmt_or_empty + SEMI + expr_or_empty + SEMI + stmt_or_empty + RPAR + stmt

    in_ = IN + num + POINT + POINT + num

    when_expr = (expr | in_) + OPERATOR + (expr | stmt)
    when = (WHEN + pp.Optional(LPAR + expr + RPAR) + LBRACE + pp.OneOrMore(when_expr) + RBRACE)

    stmt_list = pp.Forward()  # объявляем

    """stmt1 = (
            call |
            assign
    )
    stmt2 = (
            if_ |
            for_ |
            when |
            LBRACE + stmt_list + RBRACE
    )

    stmt << ((stmt1 + SEMI) | stmt2)"""

    stmt << (
            call |
            assign |
            if_ |
            for_ |
            in_ |
            when |
            LBRACE + stmt_list + RBRACE
    )
    stmt_list << pp.ZeroOrMore(stmt + pp.ZeroOrMore(SEMI))  # переопределяем
    program = stmt_list.ignore(pp.cStyleComment).ignore(pp.dblSlashComment) + pp.StringEnd()

    start = program

    def set_parse_action_magic(rule_name: str, parser: pp.ParserElement) -> None:
        if rule_name == rule_name.upper():
            return
        if getattr(parser, 'name', None) and parser.name.isidentifier():
            rule_name = parser.name
        if rule_name == 'binary':
            def bin_op_parse_action(s, loc, tocs):
                node = tocs[0]
                for i in range(1, len(tocs) - 1, 2):
                    node = BinOpNode(BinOp(tocs[i]), node, tocs[i + 1])
                return node
            parser.setParseAction(bin_op_parse_action)
        elif rule_name == 'unary':
            def un_op_parse_action(s, loc, tocs):
                return UnOpNode(UnOp(tocs[0]), tocs[1])
            parser.setParseAction(un_op_parse_action)
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


def parse(prog: str) -> StmtListNode:
    return parser.parseString(str(prog))[0]
