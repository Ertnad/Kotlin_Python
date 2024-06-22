from pathlib import Path
from typing import Any

from src import visitor
from src.mel_ast import LiteralNode, AssignNode, StmtListNode, FunDeclNode, IdentNode, ReturnNode, VarDecl, \
    BinOpNode, TypeConvertNode, CallNode, IfNode, WhileNode, ForNode
from src.code_gen_base import CodeLabel, CodeGenerator, find_vars_decls, DEFAULT_TYPE_VALUES
from src.semantic_base import BaseType, ScopeType, BinOp, TypeDesc


RUNTIME_CLASS_NAME = 'CompilerDemo.Runtime'

JBC_TYPE_NAMES = {
    BaseType.VOID: 'void',
    BaseType.INT: 'int',
    BaseType.FLOAT: 'double',
    BaseType.BOOL: 'boolean',
    BaseType.STR: 'java.lang.String'
}
JBC_TYPE_SIZES = {
    BaseType.INT: 1,
    BaseType.FLOAT: 2,
    BaseType.BOOL: 1,
    BaseType.STR: 1
}
JBC_TYPE_PREFIXES = {
    BaseType.VOID: '',
    BaseType.INT: 'i',
    BaseType.FLOAT: 'd',
    BaseType.BOOL: 'i',
    BaseType.STR: 'a'
}
JBC_COMPARE_SUFFIXES = {
    BinOp.GT: 'gt',
    BinOp.LT: 'lt',
    BinOp.GE: 'ge',
    BinOp.LE: 'le',
    BinOp.EQUALS: 'eq',
    BinOp.NEQUALS: 'ne'
}


class JbcException(Exception):
    """Класс для исключений во время генерации Java Byte Code
       (на всякий случай, пока не используется)
    """

    def __init__(self, message, **kwargs: Any) -> None:
        self.message = message


class JbcCodeGenerator(CodeGenerator):
    """Класс для генерации Java Byte Code
    """

    def __init__(self, file_name: str):
        super().__init__()
        self.file_name = file_name

    @property
    def class_name(self):
        name = Path(self.file_name).stem
        if not name[0].isidentifier():
            name = f'_{name}'
        return name

    def start(self) -> None:
        # обязательно указать версию не выше 6, иначе нужно работать со стековыми фреймами, что очень сложно
        self.add('version 6;')
        self.add(f'public class {self.class_name} extends java.lang.Object')
        self.add('{')

    def end(self) -> None:
        self.add('}')

    @visitor.on('AstNode')
    def jbc_gen(self, AstNode):
        """
        Нужен для работы модуля visitor (инициализации диспетчера)
        """
        pass

    def push_const(self, type: BaseType, value: Any) -> None:
        if type == BaseType.INT:
            self.add('ldc', value)
        elif type == BaseType.FLOAT:
            self.add('ldc2_w', f'{value:.20f}D')
        elif type == BaseType.BOOL:
            self.add(f'iconst_{1 if value else 0}')
        elif type == BaseType.STR:
            self.add('ldc', f'"{value}"')
        else:
            pass

    @visitor.when(LiteralNode)
    def jbc_gen(self, node: LiteralNode) -> None:
        self.push_const(node.node_type.base_type, node.value)

    @visitor.when(IdentNode)
    def jbc_gen(self, node: IdentNode) -> None:
        base_type = node.node_ident.type.base_type
        if node.node_ident.scope in [ScopeType.LOCAL, ScopeType.PARAM]:
            self.add(f'{JBC_TYPE_PREFIXES[base_type]}load', node.node_ident.jbc_offset)
        elif node.node_ident.scope in (ScopeType.GLOBAL, ScopeType.GLOBAL_LOCAL):
            self.add(f'getstatic {self.class_name}#{JBC_TYPE_NAMES[base_type]} _gv{node.node_ident.index}')

    @visitor.when(AssignNode)
    def jbc_gen(self, node: AssignNode) -> None:
        node.val.jbc_gen(self)
        var = node.var
        base_type = var.node_ident.type.base_type
        if var.node_ident.scope in [ScopeType.LOCAL, ScopeType.PARAM]:
            self.add(f'{JBC_TYPE_PREFIXES[base_type]}store', var.node_ident.jbc_offset)
        elif var.node_ident.scope in (ScopeType.GLOBAL, ScopeType.GLOBAL_LOCAL):
            self.add(f'putstatic {self.class_name}#{JBC_TYPE_NAMES[base_type]} _gv{var.node_ident.index}')

    @visitor.when(VarDecl)
    def jbc_gen(self, node: VarDecl) -> None:
        for var in node.vars:
            if isinstance(var, AssignNode):
                var.jbc_gen(self)

    def bool_val_gen(self, cmd: str) -> None:
        true_label = CodeLabel()
        end_label = CodeLabel()
        self.add(cmd, true_label)
        self.add(f'iconst_0')
        self.add('goto', end_label)
        self.add(true_label)
        self.add(f'iconst_1')
        self.add(end_label)

    @visitor.when(BinOpNode)
    def jbc_gen(self, node: BinOpNode) -> None:
        node.arg1.jbc_gen(self)
        node.arg2.jbc_gen(self)
        if node.op in [BinOp.EQUALS, BinOp.NEQUALS, BinOp.GT, BinOp.LT, BinOp.GE, BinOp.LE]:
            if node.arg1.node_type == TypeDesc.STR:
                self.add('invokevirtual java.lang.String#int compareTo(java.lang.String)')
                self.bool_val_gen(f'if{JBC_COMPARE_SUFFIXES[node.op]}')
            elif node.arg1.node_type == TypeDesc.FLOAT:
                self.add('dcmpg')
                self.bool_val_gen(f'if{JBC_COMPARE_SUFFIXES[node.op]}')
            else:
                self.bool_val_gen(f'if_icmp{JBC_COMPARE_SUFFIXES[node.op]}')
        elif node.op == BinOp.ADD:
            if node.arg1.node_type == TypeDesc.STR:
                self.add(f'invokestatic {RUNTIME_CLASS_NAME}#{JBC_TYPE_NAMES[BaseType.STR]} concat({JBC_TYPE_NAMES[BaseType.STR]}, {JBC_TYPE_NAMES[BaseType.STR]})')
            else:
                self.add(f'{JBC_TYPE_PREFIXES[node.arg1.node_type.base_type]}add')
        elif node.op == BinOp.SUB:
            self.add(f'{JBC_TYPE_PREFIXES[node.arg1.node_type.base_type]}sub')
        elif node.op == BinOp.MUL:
            self.add(f'{JBC_TYPE_PREFIXES[node.arg1.node_type.base_type]}mul')
        elif node.op == BinOp.DIV:
            self.add(f'{JBC_TYPE_PREFIXES[node.arg1.node_type.base_type]}div')
        elif node.op == BinOp.MOD:
            self.add(f'{JBC_TYPE_PREFIXES[node.arg1.node_type.base_type]}rem')
        elif node.op == BinOp.LOGICAL_AND:
            self.add('iand')
        elif node.op == BinOp.LOGICAL_OR:
            self.add('ior')
        elif node.op == BinOp.BIT_AND:
            self.add('iand')
        elif node.op == BinOp.BIT_OR:
            self.add('ior')
        else:
            pass

    @visitor.when(TypeConvertNode)
    def jbc_gen(self, node: TypeConvertNode) -> None:
        node.expr.jbc_gen(self)
        # часто встречаемые варианты будет реализовывать в коде, а не через класс Runtime
        if node.node_type.base_type == BaseType.FLOAT and node.expr.node_type.base_type == BaseType.INT:
            self.add('i2d')
        elif node.node_type.base_type == BaseType.BOOL and node.expr.node_type.base_type == BaseType.INT:
            false_label = CodeLabel()
            end_label = CodeLabel()
            self.add('ifeq', false_label)
            self.add(f'iconst_1')
            self.add('goto', end_label)
            self.add(false_label)
            self.add(f'iconst_0')
            self.add(end_label)
        else:
            cmd = f'invokestatic {RUNTIME_CLASS_NAME}#{JBC_TYPE_NAMES[node.node_type.base_type]} convert({JBC_TYPE_NAMES[node.expr.node_type.base_type]})'
            self.add(cmd)

    @visitor.when(CallNode)
    def jbc_gen(self, node: CallNode) -> None:
        for param in node.params:
            param.jbc_gen(self)
        class_name = RUNTIME_CLASS_NAME if node.func.node_ident.built_in else self.class_name
        param_types = ', '.join(JBC_TYPE_NAMES[param.node_type.base_type] for param in node.params)
        cmd = f'invokestatic {class_name}#{JBC_TYPE_NAMES[node.node_type.base_type]} {node.func.name}({param_types})'
        self.add(cmd)

    @visitor.when(ReturnNode)
    def jbc_gen(self, node: ReturnNode) -> None:
        node.val.jbc_gen(self)
        self.add(f'{JBC_TYPE_PREFIXES[node.val.node_type.base_type]}return')

    @visitor.when(IfNode)
    def jbc_gen(self, node: IfNode) -> None:
        else_label = CodeLabel()
        end_label = CodeLabel()
        node.cond.jbc_gen(self)
        self.add('ifeq', else_label)
        node.then_stmt.jbc_gen(self)
        self.add('goto', end_label)
        self.add(else_label)
        if node.else_stmt:
            node.else_stmt.jbc_gen(self)
        self.add(end_label)

    @visitor.when(WhileNode)
    def jbc_gen(self, node: WhileNode) -> None:
        start_label = CodeLabel()
        end_label = CodeLabel()
        self.add(start_label)
        node.cond.jbc_gen(self)
        end_label = CodeLabel()
        self.add('ifeq', end_label)
        node.body.jbc_gen(self)
        self.add('goto', start_label)
        self.add(end_label)

    @visitor.when(ForNode)
    def jbc_gen(self, node: ForNode) -> None:
        start_label = CodeLabel()
        end_label = CodeLabel()
        node.init.jbc_gen(self)
        self.add(start_label)
        node.cond.jbc_gen(self)
        self.add('ifeq', end_label)
        node.body.jbc_gen(self)
        node.step.jbc_gen(self)
        self.add('goto', start_label)
        self.add(end_label)

    @visitor.when(FunDeclNode)
    def jbc_gen(self, func: FunDeclNode) -> None:
        var_offset = 0
        params = ''
        for p in func.params:
            p.node_ident.jbc_offset = var_offset
            var_offset += JBC_TYPE_SIZES[p.type.type.base_type]
            if len(params) > 0:
                params += ', '
            params += f'{JBC_TYPE_NAMES[p.type.type.base_type]} {str(p.name.name)}'
        self.add(f'public static {JBC_TYPE_NAMES[func.type.type.base_type]} {func.name}({params})')
        self.add('{')

        local_vars_decls = find_vars_decls(func)
        for node in local_vars_decls:
            for var in node.vars:
                if isinstance(var, AssignNode):
                    var = var.var
                if var.node_ident.scope in (ScopeType.LOCAL, ):
                    var.node_ident.jbc_offset = var_offset
                    var_offset += JBC_TYPE_SIZES[var.node_type.base_type]

        func.body.jbc_gen(self)

        # при необходимости добавим return
        if not (isinstance(func.body, ReturnNode) or
                len(func.body.childs) > 0 and isinstance(func.body.childs[-1], ReturnNode)):
            if func.type.type.base_type != BaseType.VOID:
                self.push_const(func.type.type.base_type, DEFAULT_TYPE_VALUES[func.type.type.base_type])
            self.add(f'{JBC_TYPE_PREFIXES[func.type.type.base_type]}return')

        self.add('}')

    @visitor.when(StmtListNode)
    def jbc_gen(self, node: StmtListNode) -> None:
        for stmt in node.stmts:
            stmt.jbc_gen(self)

    def gen_program(self, prog: StmtListNode):
        self.start()
        global_vars_decls = find_vars_decls(prog)
        for node in global_vars_decls:
            for var in node.vars:
                if isinstance(var, AssignNode):
                    var = var.var
                if var.node_ident.scope in (ScopeType.GLOBAL, ScopeType.GLOBAL_LOCAL):
                    self.add(f'public static {JBC_TYPE_NAMES[var.node_type.base_type]} _gv{var.node_ident.index};')
        for stmt in prog.stmts:
            if isinstance(stmt, FunDeclNode):
                self.jbc_gen(stmt)
        self.add('')
        self.add('public static void main(java.lang.String[])')
        self.add('{')
        for stmt in prog.childs:
            if not isinstance(stmt, FunDeclNode):
                self.jbc_gen(stmt)

        # т.к. "глобальный" код будет функцией, обязательно надо добавить ret
        self.add('return')

        self.add('}')
        self.end()
