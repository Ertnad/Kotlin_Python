from abc import ABC, abstractmethod
from contextlib import suppress
from enum import Enum
from typing import Callable, Tuple, Optional, Any, Union

from src.semantic_base import IdentDesc, TypeDesc, SemanticException, IdentScope, TYPE_CONVERTIBILITY


class AstNode(ABC):
    init_action: Callable[['AstNode'], None] = None

    def __init__(self, row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__()
        self.row = row
        self.col = col
        for k, v in props.items():
            setattr(self, k, v)
        if AstNode.init_action is not None:
            AstNode.init_action(self)
        self.node_type: Optional[TypeDesc] = None
        self.node_ident: Optional[IdentDesc] = None

    @property
    def childs(self) -> Tuple['AstNode', ...]:
        return ()

    @abstractmethod
    def __str__(self) -> str:
        pass

    @property
    def tree(self) -> [str, ...]:
        res = [str(self)]
        childs = self.childs
        for i, child in enumerate(childs):
            ch0, ch = '├', '│'
            if i == len(childs) - 1:
                ch0, ch = '└', ' '
            res.extend(((ch0 if j == 0 else ch) + ' ' + s for j, s in enumerate(child.tree)))
        return res

    def visit(self, func: Callable[['AstNode'], None]) -> None:
        func(self)
        map(func, self.childs)

    def to_str(self):
        return str(self)

    def to_str_full(self):
        r = ''
        if self.node_ident:
            r = str(self.node_ident)
        elif self.node_type:
            r = str(self.node_type)
        return self.to_str() + (' : ' + r if r else '')

    def semantic_error(self, message: str):
        raise SemanticException(message, self.row, self.col)

    """Чтобы среда не "ругалась" в модуле semantic_checker
    """

    def semantic_check(self, checker, scope: IdentScope) -> None:
        checker.semantic_check(self, scope)

    def __getitem__(self, index):
        return self.childs[index] if index < len(self.childs) else None


class ExprNode(AstNode):
    pass


class LiteralNode(ExprNode):
    def __init__(self, literal: str,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.literal = literal
        if literal in ('true', 'false'):
            self.value = bool(literal)
        else:
            self.value = eval(literal)

    def __str__(self) -> str:
        return self.literal


class NumNode(ExprNode):
    def __init__(self, num: float,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.num = float(num)

    def __str__(self) -> str:
        return str(self.num)


class IntNumNode(ExprNode):
    def __init__(self, num: int, row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.num = int(num)

    def __str__(self) -> str:
        return str(self.num)


class IdentNode(ExprNode):
    def __init__(self, name: str, row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.name = str(name)

    def __str__(self) -> str:
        return str(self.name)


class TypeNode(IdentNode):
    """Класс для представления в AST-дереве типов данный
       (при появлении составных типов данных должен быть расширен)
    """

    def __init__(self, name: str, row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(name, row=row, col=col, **props)
        self.type = None
        with suppress(SemanticException):
            self.type = TypeDesc.from_str(name)

    def to_str_full(self):
        return self.to_str()


class CallNode(ExprNode):
    def __init__(self, func: IdentNode, *params: ExprNode,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.func = func
        self.params = params

    # def childs(self) -> Tuple[IdentNode, ExprNode]:
    @property
    def childs(self) -> Tuple[IdentNode, ...]:
        return self.func, *self.params

    def __str__(self) -> str:
        return 'call'


class _GroupNode(AstNode):
    """Класс для группировки других узлов (вспомогательный, в синтаксисе нет соотвествия)
    """

    def __init__(self, name: str, *childs: AstNode,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.name = name
        self._childs = childs

    def __str__(self) -> str:
        return self.name

    @property
    def childs(self) -> Tuple['AstNode', ...]:
        return self._childs


class TypeConvertNode(ExprNode):
    """Класс для представления в AST-дереве операций конвертации типов данных
       (в языке программирования может быть как expression, так и statement)
    """

    def __init__(self, expr: ExprNode, type_: TypeDesc,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.expr = expr
        self.type = type_
        self.node_type = type_

    def __str__(self) -> str:
        return 'convert'

    @property
    def childs(self) -> Tuple[AstNode, ...]:
        return (_GroupNode(str(self.type), self.expr),)


def type_convert(expr: ExprNode, type_: TypeDesc, except_node: Optional[AstNode] = None,
                 comment: Optional[str] = None) -> ExprNode:
    """Метод преобразования ExprNode узла AST-дерева к другому типу
    :param expr: узел AST-дерева
    :param type_: требуемый тип
    :param except_node: узел, о которого будет исключение
    :param comment: комментарий
    :return: узел AST-дерева c операцией преобразования
    """

    if expr.node_type is None:
        except_node.semantic_error('Тип выражения не определен')
    if expr.node_type == type_:
        return expr
    if expr.node_type.is_simple and type_.is_simple and \
            expr.node_type.base_type in TYPE_CONVERTIBILITY and type_.base_type in TYPE_CONVERTIBILITY[
        expr.node_type.base_type]:
        return TypeConvertNode(expr, type_)
    else:
        (except_node if except_node else expr).semantic_error('Тип {0}{2} не конвертируется в {1}'.format(
            expr.node_type, type_, ' ({})'.format(comment) if comment else ''
        ))


class ReturnNode(ExprNode):
    def __init__(self, func: IdentNode, *params: ExprNode, row: Optional[int] = None, col: Optional[int] = None,
                 **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.func = func
        self.params = params

    @property
    def childs(self) -> Tuple[IdentNode, ExprNode]:
        return self.func, *self.params

    def __str__(self) -> str:
        return 'return'


class UnOp(Enum):
    NOT = '!'


class BinOp(Enum):
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'
    GE = '>='
    LE = '<='
    GT = '>'
    LT = '<'
    EQUALS = '=='
    NOTEQUALS = '!='
    LOGIC_AND = '&&'
    LOGIC_OR = '||'


class Op(Enum):
    IN = 'in'


class UnOpNode(ExprNode):
    def __init__(self, op: UnOp, arg1: ExprNode,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.op = op
        self.arg1 = arg1

    @property
    def childs(self) -> Tuple[ExprNode]:
        return self.arg1,

    def __str__(self) -> str:
        return str(self.op.value)


class BinOpNode(ExprNode):
    def __init__(self, op: BinOp, arg1: ExprNode, arg2: ExprNode,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2

    @property
    def childs(self) -> Tuple[ExprNode, ExprNode]:
        return self.arg1, self.arg2

    def __str__(self) -> str:
        return str(self.op.value)


class StmtNode(AstNode):
    def to_str_full(self):
        return self.to_str()


class AssignNode(StmtNode):
    def __init__(self, var: IdentNode, val: ExprNode,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.var = var
        self.val = val

    def __str__(self) -> str:
        return '='

    @property
    def childs(self) -> Tuple[IdentNode, ExprNode]:
        return self.var, self.val


class VarsNode(StmtNode):
    """Класс для представления в AST-дереве объявления переменнных
    """

    def __init__(self, type_: TypeNode, *vars_: Union[IdentNode, 'AssignNode'],
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.type = type_
        self.vars = vars_

    def __str__(self) -> str:
        return str(self.type)

    @property
    def childs(self) -> Tuple[AstNode, ...]:
        return self.vars


class IfNode(StmtNode):
    def __init__(self, cond: ExprNode, then_stmt: StmtNode, else_stmt: Optional[StmtNode] = None,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.cond = cond
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt

    def __str__(self) -> str:
        return 'if'

    @property
    def childs(self) -> Tuple[ExprNode, StmtNode, Optional[StmtNode]]:
        return self.cond, self.then_stmt, *((self.else_stmt,) if self.else_stmt else tuple())


class ForNode(StmtNode):
    def __init__(self, assign: Optional[ExprNode], cond: Optional[ExprNode], step: Optional[StmtNode],
                 body: Optional[StmtNode], row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.assign = assign if assign else EMPTY_STMT
        self.cond = cond if cond else EMPTY_STMT
        self.step = step if step else EMPTY_STMT
        self.body = body if body else EMPTY_STMT

    @property
    def childs(self) -> Tuple[AstNode, ...]:
        return self.assign, self.cond, self.step, self.body

    def __str__(self) -> str:
        return 'for'


class InNode(ExprNode):
    def __init__(self, arg1: IntNumNode, arg2: IntNumNode,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.arg1 = arg1
        self.arg2 = arg2

    @property
    def childs(self) -> Tuple[IntNumNode, IntNumNode]:
        return self.arg1, self.arg2

    def __str__(self) -> str:
        return 'in'


class WhenExprNode(StmtNode):
    def __init__(self, cond: ExprNode, then_stmt: StmtNode,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.cond = cond
        self.then_stmt = then_stmt

    @property
    def childs(self) -> Tuple[ExprNode, StmtNode]:
        return self.cond if self.cond else tuple(), self.then_stmt

    def __str__(self) -> str:
        return '->'


class WhileNode(StmtNode):
    def __init__(self, cond: ExprNode, *when_expr: WhenExprNode,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.cond = cond
        self.when_expr = when_expr

    @property
    def childs(self) -> tuple[ExprNode, Any]:
        return self.cond, *self.when_expr

    def __str__(self) -> str:
        return 'while'


class WhenNode(StmtNode):
    def __init__(self, cond: ExprNode, *when_expr: WhenExprNode, else_stmt: Optional[StmtNode] = None,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.cond = cond
        self.when_expr = when_expr
        self.else_stmt = else_stmt

    @property
    def childs(self) -> tuple[ExprNode, Any]:
        return self.cond, *self.when_expr + ((self.else_stmt,) if self.else_stmt else tuple())

    def __str__(self) -> str:
        return 'when'


class VarDecl(StmtNode):
    def __init__(self, const: bool, name: IdentNode, type_: Optional[IdentNode], value: Optional[ExprNode],
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.const = const
        self.name = name
        self.type_ = type_
        self.value = value

    @property
    def childs(self) -> Tuple[AstNode]:
        return (self.value,) if self.value else ()

    def __str__(self) -> str:
        return f'{"val" if self.const else "var"} {self.name}{": " + str(self.type_) if self.type_ else ""}'


class FunParamNode(ExprNode):
    def __init__(self, name: TypeNode, type_: IdentNode,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.name = name
        self.type_ = type_

    @property
    def childs(self) -> Tuple[IdentNode, IdentNode]:
        return self.name, self.type_

    def __str__(self) -> str:
        return f"{self.name}: {self.type_}"


class StmtListNode(StmtNode):
    """Класс для представления в AST-дереве последовательности инструкций
    """

    def __init__(self, *exprs: StmtNode,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.exprs = exprs
        self.program = False

    def __str__(self) -> str:
        return '...'

    @property
    def childs(self) -> Tuple[StmtNode, ...]:
        return self.exprs

    def semantic_check(self, scope: IdentScope) -> None:
        if not self.program:
            scope = IdentScope(scope)
        for expr in self.exprs:
            expr.semantic_check(scope)
        self.node_type = TypeDesc.VOID

class FunBodyNode(AstNode):
    def __init__(self, *exprs: AstNode,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.exprs = exprs

    @property
    def childs(self) -> tuple[AstNode, ...]:
        return self.exprs

    def __str__(self) -> str:
        return '...'


class FunDeclNode(ExprNode):
    def __init__(self, name: IdentNode, *params_and_type_and_body: Union[FunParamNode, IdentNode, StmtListNode],
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.name = name
        self.params = params_and_type_and_body[:-2]
        self.return_type = params_and_type_and_body[-2]
        self.body = params_and_type_and_body[-1]

    @property
    def childs(self) -> Tuple[FunParamNode, StmtListNode]:
        return *self.params, self.body

    def __str__(self) -> str:
        return f'fun {self.name} : {self.return_type} ()'


class FunCallWithBodyNode(ExprNode):
    def __init__(self, func: IdentNode, body: StmtListNode):
        super().__init__()
        self.func = func
        self.body = body

    @property
    def childs(self) -> Tuple[IdentNode, StmtListNode]:
        return self.func, self.body

    def __str__(self) -> str:
        return f'call'


class ContinueNode(StmtNode):
    def __str__(self) -> str:
        return 'continue'


class BreakNode(StmtNode):
    def __str__(self) -> str:
        return 'break'


EMPTY_STMT = StmtListNode()
EMPTY_IDENT = IdentDesc('', TypeDesc.VOID)
