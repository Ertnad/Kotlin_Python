from abc import ABC, abstractmethod
from typing import Callable, Tuple, Optional, Union
from enum import Enum


class AstNode(ABC):
    @property
    def childs(self)->Tuple['AstNode', ...]:
        return ()

    @abstractmethod
    def __str__(self)->str:
        pass

    @property
    def tree(self)->[str, ...]:
        res = [str(self)]
        childs = self.childs
        for i, child in enumerate(childs):
            ch0, ch = '├', '│'
            if i == len(childs) - 1:
                ch0, ch = '└', ' '
            res.extend(((ch0 if j == 0 else ch) + ' ' + s for j, s in enumerate(child.tree)))
        return res

    def visit(self, func: Callable[['AstNode'], None])->None:
        func(self)
        map(func, self.childs)

    def __getitem__(self, index):
        return self.childs[index] if index < len(self.childs) else None


class ExprNode(AstNode):
    pass


class literalNode(ExprNode):
    pass


class NumNode(literalNode):
    def __init__(self, num: float):
        super().__init__()
        self.num = float(num)

    def __str__(self)->str:
        return str(self.num)


class IdentNode(ExprNode):
    def __init__(self, name: str):
        super().__init__()
        self.name = str(name)

    def __str__(self) -> str:
        return str(self.name)


class CallNode(ExprNode):
    def __init__(self, func: IdentNode, *params: ExprNode):
        super().__init__()
        self.func = func
        self.params = params

    @property
    def childs(self) -> Tuple[IdentNode, ExprNode]:
        return self.func, *self.params

    def __str__(self) -> str:
        return 'call'


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
    def __init__(self, op: UnOp, arg1: ExprNode):
        super().__init__()
        self.op = op
        self.arg1 = arg1

    @property
    def childs(self) -> Tuple[ExprNode]:
        return self.arg1,

    def __str__(self) -> str:
        return str(self.op.value)


class BinOpNode(ExprNode):
    def __init__(self, op: BinOp, arg1: ExprNode, arg2: ExprNode):
        super().__init__()
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2

    @property
    def childs(self) -> Tuple[ExprNode, ExprNode]:
        return self.arg1, self.arg2

    def __str__(self) -> str:
        return str(self.op.value)


class StmtNode(AstNode):
    pass


class AssignNode(StmtNode):
    def __init__(self, var: IdentNode, val: ExprNode):
        super().__init__()
        self.var = var
        self.val = val

    @property
    def childs(self) -> Tuple[IdentNode, ExprNode]:
        return self.var, self.val

    def __str__(self) -> str:
        return '='


class IfNode(StmtNode):
    def __init__(self, cond: ExprNode, then_stmt: StmtNode, else_stmt: Optional[StmtNode] = None):
        super().__init__()
        self.cond = cond
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt

    @property
    def childs(self) -> Tuple[ExprNode, StmtNode, Optional[StmtNode]]:
        return (self.cond, self.then_stmt) + ((self.else_stmt,) if self.else_stmt else tuple())

    def __str__(self) -> str:
        return 'if'


class ForNode(StmtNode):
    def __init__(self, assign: Optional[ExprNode], cond: Optional[ExprNode], step: Optional[StmtNode],
                 body: Optional[StmtNode]):
        super().__init__()
        self.assign = assign
        self.cond = cond
        self.step = step
        self.body = body

    @property
    def childs(self) -> Tuple[Optional[StmtNode], Optional[ExprNode], Optional[StmtNode], Optional[StmtNode]]:
        return self.assign, self.cond, self.step, self.body

    def __str__(self) -> str:
        return 'for'


class InNode(ExprNode):
    def __init__(self, arg1: NumNode, arg2: NumNode):
        super().__init__()
        self.arg1 = arg1
        self.arg2 = arg2

    @property
    def childs(self) -> Tuple[NumNode, NumNode]:
        return self.arg1, self.arg2

    def __str__(self) -> str:
        return 'in'


class WhenExprNode(StmtNode):
    def __init__(self, cond: ExprNode, then_stmt: StmtNode):
        super().__init__()
        self.cond = cond
        self.then_stmt = then_stmt

    @property
    def childs(self) -> Tuple[ExprNode, StmtNode]:
        return self.cond if self.cond else tuple(), self.then_stmt

    def __str__(self) -> str:
        return '->'


class WhenNode(StmtNode):
    def __init__(self, cond: ExprNode, *when_expr: WhenExprNode):
        super().__init__()
        self.cond = cond
        self.when_expr = when_expr

    @property
    def childs(self) -> tuple[ExprNode, WhenExprNode]:
        return self.cond, *self.when_expr

    def __str__(self) -> str:
        return 'when'


class StmtListNode(AstNode):
    def __init__(self, *exprs: AstNode):
        super().__init__()
        self.exprs = exprs

    @property
    def childs(self) -> Tuple[AstNode]:
        return self.exprs

    def __str__(self) -> str:
        return '...'
