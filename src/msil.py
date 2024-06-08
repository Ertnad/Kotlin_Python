from typing import List, Union, Any

from src import visitor
from src.semantic_base import BaseType, TypeDesc, ScopeType, BinOp
from src.mel_ast import AstNode, LiteralNode, IdentNode, BinOpNode, TypeConvertNode, CallNode, \
    VarDecl, AssignNode, ReturnNode, IfNode, ForNode, StmtListNode, WhileNode, FunDeclNode
from src.code_gen_base import CodeLabel, CodeLine, CodeGenerator, find_vars_decls, DEFAULT_TYPE_VALUES


RUNTIME_CLASS_NAME = 'CompilerDemo.Runtime'
PROGRAM_CLASS_NAME = 'Program'

MSIL_TYPE_NAMES = {
    BaseType.VOID: 'void',
    BaseType.INT: 'int32',
    BaseType.FLOAT: 'float64',
    BaseType.BOOL: 'bool',
    BaseType.STR: 'string'
}


class MsilException(Exception):
    """Класс для исключений во время генерации MSIL
       (на всякий случай, пока не используется)
    """

    def __init__(self, message, **kwargs: Any) -> None:
        self.message = message


class MsilCodeGenerator(CodeGenerator):
    """Класс для генерации MSIL-кода
    """

    def start(self) -> None:
        self.add('.assembly program')
        self.add('{')
        self.add('}')
        self.add(f'.class public {PROGRAM_CLASS_NAME}')
        self.add('{')

    def end(self) -> None:
        self.add('}')

    @visitor.on('AstNode')
    def msil_gen(self, AstNode):
        """
        Нужен для работы модуля visitor (инициализации диспетчера)
        """
        pass

    def push_const(self, type: BaseType, value: Any) -> None:
        if type == BaseType.INT:
            self.add('ldc.i4', value)
        elif type == BaseType.FLOAT:
            self.add('ldc.r8', str(value))
        elif type == BaseType.BOOL:
            self.add('ldc.i4', 1 if value else 0)
        elif type == BaseType.STR:
            self.add(f'ldstr "{value}"')
        else:
            pass

    @visitor.when(LiteralNode)
    def msil_gen(self, node: LiteralNode) -> None:
        self.push_const(node.node_type.base_type, node.value)

    @visitor.when(IdentNode)
    def msil_gen(self, node: IdentNode) -> None:
        if node.node_ident.scope == ScopeType.LOCAL:
            self.add('ldloc', node.node_ident.index)
        elif node.node_ident.scope == ScopeType.PARAM:
            self.add('ldarg', node.node_ident.index)
        elif node.node_ident.scope in (ScopeType.GLOBAL, ScopeType.GLOBAL_LOCAL):
            self.add(f'ldsfld {MSIL_TYPE_NAMES[node.node_ident.type.base_type]} {PROGRAM_CLASS_NAME}::_gv{node.node_ident.index}')

    @visitor.when(AssignNode)
    def msil_gen(self, node: AssignNode) -> None:
        node.val.msil_gen(self)
        var = node.var
        if var.node_ident.scope == ScopeType.LOCAL:
            self.add('stloc', var.node_ident.index)
        elif var.node_ident.scope == ScopeType.PARAM:
            self.add('starg', var.node_ident.index)
        elif var.node_ident.scope in (ScopeType.GLOBAL, ScopeType.GLOBAL_LOCAL):
            self.add(f'stsfld {MSIL_TYPE_NAMES[var.node_ident.type.base_type]} Program::_gv{var.node_ident.index}')

    @visitor.when(VarDecl)
    def msil_gen(self, node: VarDecl) -> None:
        if isinstance(node, AssignNode):
            node.msil_gen(self)

    @visitor.when(BinOpNode)
    def msil_gen(self, node: BinOpNode) -> None:
        node.arg1.msil_gen(self)
        node.arg2.msil_gen(self)
        if node.op == BinOp.NEQUALS:
            if node.arg1.node_type == TypeDesc.STR:
                self.add('call bool [mscorlib]System.String::op_Inequality(string, string)')
            else:
                self.add('ceq')
                self.add('ldc.i4.0')
                self.add('ceq')
        if node.op == BinOp.EQUALS:
            if node.arg1.node_type == TypeDesc.STR:
                self.add('call bool [mscorlib]System.String::op_Equality(string, string)')
            else:
                self.add('ceq')
        elif node.op == BinOp.GT:
            if node.arg1.node_type == TypeDesc.STR:
                self.add(f'call {MSIL_TYPE_NAMES[BaseType.INT]} class {RUNTIME_CLASS_NAME}::compare({MSIL_TYPE_NAMES[BaseType.STR]}, {MSIL_TYPE_NAMES[BaseType.STR]})')
                self.add('ldc.i4.0')
                self.add('cgt')
            else:
                self.add('cgt')
        elif node.op == BinOp.LT:
            if node.arg1.node_type == TypeDesc.STR:
                self.add(f'call {MSIL_TYPE_NAMES[BaseType.INT]} class {RUNTIME_CLASS_NAME}::compare({MSIL_TYPE_NAMES[BaseType.STR]}, {MSIL_TYPE_NAMES[BaseType.STR]})')
                self.add('ldc.i4.0')
                self.add('clt')
            else:
                self.add('clt')
        elif node.op == BinOp.GE:
            if node.arg1.node_type == TypeDesc.STR:
                self.add(f'call {MSIL_TYPE_NAMES[BaseType.INT]} class {RUNTIME_CLASS_NAME}::compare({MSIL_TYPE_NAMES[BaseType.STR]}, {MSIL_TYPE_NAMES[BaseType.STR]})')
                self.add('ldc.i4', '-1')
                self.add('cgt')
            else:
                self.add('clt')
                self.add('ldc.i4.0')
                self.add('ceq')
        elif node.op == BinOp.LE:
            if node.arg1.node_type == TypeDesc.STR:
                self.add(f'call {MSIL_TYPE_NAMES[BaseType.INT]} class {RUNTIME_CLASS_NAME}::compare({MSIL_TYPE_NAMES[BaseType.STR]}, {MSIL_TYPE_NAMES[BaseType.STR]})')
                self.add('ldc.i4.1')
                self.add('clt')
            else:
                self.add('cgt')
                self.add('ldc.i4.0')
                self.add('ceq')
        elif node.op == BinOp.ADD:
            if node.arg1.node_type == TypeDesc.STR:
                self.add(f'call {MSIL_TYPE_NAMES[BaseType.STR]} class {RUNTIME_CLASS_NAME}::concat({MSIL_TYPE_NAMES[BaseType.STR]}, {MSIL_TYPE_NAMES[BaseType.STR]})')
            else:
                self.add('add')
        elif node.op == BinOp.SUB:
            self.add('sub')
        elif node.op == BinOp.MUL:
            self.add('mul')
        elif node.op == BinOp.DIV:
            self.add('div')
        elif node.op == BinOp.MOD:
            self.add('rem')
        elif node.op == BinOp.LOGICAL_AND:
            self.add('and')
        elif node.op == BinOp.LOGICAL_OR:
            self.add('or')
        elif node.op == BinOp.BIT_AND:
            self.add('and')
        elif node.op == BinOp.BIT_OR:
            self.add('or')
        else:
            pass

    @visitor.when(TypeConvertNode)
    def msil_gen(self, node: TypeConvertNode) -> None:
        node.expr.msil_gen(self)
        # часто встречаемые варианты будет реализовывать в коде, а не через класс Runtime
        if node.node_type.base_type == BaseType.FLOAT and node.expr.node_type.base_type == BaseType.INT:
            self.add('conv.r8')
        elif node.node_type.base_type == BaseType.BOOL and node.expr.node_type.base_type == BaseType.INT:
            self.add('ldc.i4.0')
            self.add('ceq')
            self.add('ldc.i4.0')
            self.add('ceq')
        else:
            cmd = f'call {MSIL_TYPE_NAMES[node.node_type.base_type]} class {RUNTIME_CLASS_NAME}::convert({MSIL_TYPE_NAMES[node.expr.node_type.base_type]})'
            self.add(cmd)

    @visitor.when(CallNode)
    def msil_gen(self, node: CallNode) -> None:
        for param in node.params:
            param.msil_gen(self)
        class_name = RUNTIME_CLASS_NAME if node.func.node_ident.built_in else PROGRAM_CLASS_NAME
        param_types = ', '.join(MSIL_TYPE_NAMES[param.node_type.base_type] for param in node.params)
        cmd = f'call {MSIL_TYPE_NAMES[node.node_type.base_type]} class {class_name}::{node.func.name}({param_types})'
        self.add(cmd)

    @visitor.when(ReturnNode)
    def msil_gen(self, node: ReturnNode) -> None:
        node.val.msil_gen(self)
        self.add('ret')

    @visitor.when(IfNode)
    def msil_gen(self, node: IfNode) -> None:
        else_label = CodeLabel()
        end_label = CodeLabel()
        node.cond.msil_gen(self)
        self.add('brfalse', else_label)
        node.then_stmt.msil_gen(self)
        self.add('br', end_label)
        self.add(else_label)
        if node.else_stmt:
            node.else_stmt.msil_gen(self)
        self.add(end_label)

    @visitor.when(WhileNode)
    def msil_gen(self, node: WhileNode) -> None:
        start_label = CodeLabel()
        end_label = CodeLabel()
        self.add(start_label)
        node.cond.msil_gen(self)
        end_label = CodeLabel()
        self.add('brfalse', end_label)
        node.body.msil_gen(self)
        self.add('br', start_label)
        self.add(end_label)

    @visitor.when(ForNode)
    def msil_gen(self, node: ForNode) -> None:
        start_label = CodeLabel()
        end_label = CodeLabel()
        node.assign.msil_gen(self)
        self.add(start_label)
        node.cond.msil_gen(self)
        self.add('brfalse', end_label)
        node.body.msil_gen(self)
        node.step.msil_gen(self)
        self.add('br', start_label)
        self.add(end_label)

    @visitor.when(FunDeclNode)
    def msil_gen(self, func: FunDeclNode) -> None:
        params = ''
        for p in func.params:
            if len(params) > 0:
                params += ', '
            params += f'{MSIL_TYPE_NAMES[p.node_ident.type.base_type]} {str(p.name.name)}'
            # params += f'{MSIL_TYPE_NAMES[p.node_type.base_type]} {str(p.name.name)}'
        # self.add(f'.method public static {MSIL_TYPE_NAMES[func.return_type.type.base_type]} {func.name}({params}) cil managed')
        self.add(f'.method public static {MSIL_TYPE_NAMES[func.return_type.type.base_type]} {func.name.name}({params}) cil managed')
        self.add('{')

        local_vars_decls = find_vars_decls(func)
        decl = '.locals init ('
        count = 0
        for node in local_vars_decls:
            for var in node.vars:
                if isinstance(var, AssignNode):
                    var = var.var
                if var.node_ident.scope in (ScopeType.LOCAL, ):
                    if count > 0:
                        decl += ', '
                    decl += f'{MSIL_TYPE_NAMES[var.node_type.base_type]} _v{var.node_ident.index}'
                    count += 1
        decl += ')'
        if count > 0:
            self.add(decl)

        func.body.msil_gen(self)

        # при необходимости добавим ret
        if not (isinstance(func.body, ReturnNode) or
                len(func.body.childs) > 0 and isinstance(func.body.childs[-1], ReturnNode)):
            if func.type.type.base_type != BaseType.VOID:
                self.push_const(func.type.type.base_type, DEFAULT_TYPE_VALUES[func.type.type.base_type])
            self.add('ret')

        self.add('}')

    @visitor.when(StmtListNode)
    def msil_gen(self, node: StmtListNode) -> None:
        for stmt in node.stmts:
            stmt.msil_gen(self)

    def gen_program(self, prog: StmtListNode):
        self.start()
        global_vars_decls = find_vars_decls(prog)
        for node in global_vars_decls:
            if isinstance(node, AssignNode):
                node = node.var
            if node.name.node_ident.scope in (ScopeType.GLOBAL, ScopeType.GLOBAL_LOCAL):
                self.add(f'.field public static {MSIL_TYPE_NAMES[node.name.node_ident.type.base_type]} _gv{node.name.node_ident.index}')
        for stmt in prog.stmts:
            if isinstance(stmt, FunDeclNode):
                self.msil_gen(stmt)
        self.add('')
        self.add('.method public static void Main()')
        self.add('{')
        self.add('.entrypoint')
        for stmt in prog.childs:
            if not isinstance(stmt, FunDeclNode):
                self.msil_gen(stmt)

        # т.к. "глобальный" код будет функцией, обязательно надо добавить ret
        self.add('ret')

        self.add('}')
        self.end()
