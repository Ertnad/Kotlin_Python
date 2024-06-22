import inspect

import pyparsing as pp
from pyparsing import pyparsing_common as ppc

from src.mel_ast import *


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
    # EACH = pp.Keyword('each').suppress()
    IN = pp.Keyword('in').suppress()
    CONTINUE = pp.Keyword('continue').suppress()
    BREAK = pp.Keyword('break').suppress()
    RETURN = pp.Keyword('return').suppress()
    TRUE, FALSE = pp.Keyword('true').suppress(), pp.Keyword('false').suppress()

    VAL = pp.Keyword('val')
    VAR = pp.Keyword("var")
    FUN = pp.Keyword("fun").suppress()

    keywords = IF | ELSE | WHILE | WHEN | FOR | IN | VAL | VAR | FUN | RETURN

    int_num = ppc.number.copy().setName("int_num")
    num = ppc.fnumber.copy().setName('num')
    ident = (~keywords + ppc.identifier.copy()).setName('ident')  # ~ переопределён для парсера и означает не keywords
    type_ = ident.copy().setName('type')

    in_ = pp.Forward()
    expr = pp.Forward()
    return_ = pp.Forward()
    params = pp.Optional(expr + pp.ZeroOrMore(COMMA + expr))
    call = (ident + LPAR + params + RPAR)  # | (ident + LPAR + pp.Optional(ident + COLON + ident) + pp.ZeroOrMore(COMMA + ident + COLON + ident) + RPAR)
    group = call | ident | int_num | num | LPAR + expr + RPAR | in_
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

    def var_inner_parse_action(s, loc, tocs):
        const = str(tocs[0]) == 'val'
        return VarDecl(const, tocs[1], tocs[2], tocs[3]) if len(tocs) == 4 else VarDecl(const, tocs[1], tocs[2], None)

    # var_inner = ((VAR | VAL) + ident + COLON.suppress() + ident + pp.Optional(ASSIGN.suppress() + expr)).setParseAction(var_inner_parse_action)
    var_inner = ((VAR | VAL) + ident + COLON.suppress() + type_ + pp.Optional(ASSIGN.suppress() + expr)).setParseAction(
        var_inner_parse_action)

    if_ = pp.Forward()
    when = pp.Forward()
    assign = ident + ASSIGN.suppress() + (expr | if_ | when)

    if_ << ((IF + LPAR + expr + RPAR + stmt + pp.Optional(ELSE + stmt))
            | (IF + LPAR + expr + RPAR + (ident | expr) + ELSE + (ident | expr | stmt)))

    while_ = pp.Forward()

    while_ << (WHILE + LPAR + expr + RPAR + (stmt | (LBRACE + stmt + RBRACE))).setName("while")

    for_ = FOR + LPAR + stmt_or_empty + SEMI + expr_or_empty + SEMI + stmt_or_empty + RPAR + stmt

    each_expr = pp.Forward()
    iter_expr = ident + IN + expr
    each_expr << (FOR + LPAR + iter_expr + RPAR + stmt)

    in_ << IN + int_num + POINT + int_num

    when_expr = (expr | in_) + OPERATOR + (expr | stmt)
    when << (WHEN + pp.Optional(LPAR + expr + RPAR) + LBRACE + pp.OneOrMore(when_expr)
             + pp.Optional(ELSE + OPERATOR + (expr | stmt)) + RBRACE)

    stmt_list = pp.Forward()  # объявляем

    return_ << RETURN + expr_or_empty

    empty_as_void = pp.Group(pp.empty).setParseAction(lambda s, loc, tocs: TypeNode('void'))
    fun_param = ident + COLON + type_
    # params_ident = (ident + LPAR + pp.Optional(fun_params + pp.ZeroOrMore(COMMA + fun_params)) + RPAR)
    # название([пар1: тип, ...])[: тип]
    # func_param = pp.Optional(fun_param + pp.ZeroOrMore(COMMA + fun_param))
    # fun

    fun_body = stmt_list
    fun_decl = (FUN + ident + LPAR + pp.Optional(fun_param + pp.ZeroOrMore(COMMA + fun_param))
                + RPAR + ((COLON + type_) | empty_as_void) + LBRACE + fun_body + RBRACE)

    stmt << (
            call |
            assign |
            if_ |
            for_ |
            each_expr |
            when |
            var_inner |
            fun_decl |
            while_ |
            return_ |
            LBRACE + stmt_list + RBRACE |
            CONTINUE |
            BREAK  # добавляем новые операторы
    )

    stmt_list << pp.ZeroOrMore(stmt + pp.Optional(SEMI))  # переопределяем

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
                    node = BinOpNode(BinOp(tocs[i]), node, tocs[i + 1], loc=loc)
                return node

            parser.setParseAction(bin_op_parse_action)
        elif rule_name == 'unary':
            def un_op_parse_action(s, loc, tocs):
                return UnOpNode(UnOp(tocs[0]), tocs[1], loc=loc)

            parser.setParseAction(un_op_parse_action)
        else:
            cls = ''.join(x.capitalize() for x in rule_name.split('_')) + 'Node'
            with suppress(NameError):
                cls = eval(cls)
                if not inspect.isabstract(cls):
                    def parse_action(s, loc, tocs):
                        return cls(*tocs, loc=loc)

                    parser.setParseAction(parse_action)

    for var_name, value in locals().copy().items():
        if isinstance(value, pp.ParserElement):
            set_parse_action_magic(var_name, value)

    return start


parser = _make_parser()


def parse(prog: str) -> StmtListNode:
    locs = []
    row, col = 0, 0
    for ch in prog:
        if ch == '\n':
            row += 1
            col = 0
        elif ch == '\r':
            pass
        else:
            col += 1
        locs.append((row, col))

    old_init_action = AstNode.init_action

    def init_action(node: AstNode) -> None:
        loc = getattr(node, 'loc', None)
        # print('loc: ', loc)
        if isinstance(loc, int):
            node.row = locs[loc][0] + 1
            node.col = locs[loc][1] + 1

    AstNode.init_action = init_action
    try:
        prog: StmtListNode = parser.parseString(str(prog))[0]
        prog.program = True
        return prog
    finally:
        AstNode.init_action = old_init_action
