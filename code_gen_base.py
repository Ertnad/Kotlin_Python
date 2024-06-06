from typing import List, Union

from src.mel_ast import AstNode, VarsNode
from src.semantic_base import BaseType


DEFAULT_TYPE_VALUES = {
    BaseType.INT: 0,
    BaseType.FLOAT: 0.0,
    BaseType.BOOL: False,
    BaseType.STR: ''
}


class CodeLabel:
    def __init__(self, prefix: str = 'L'):
        self.index = None
        self.prefix = prefix

    def __str__(self):
        return f'{self.prefix}_{self.index}'


class CodeLine:
    def __init__(self, code: Union[str, CodeLabel], *params: Union[str, CodeLabel], label: CodeLabel = None, indent: str = None):
        if isinstance(code, CodeLabel):
            code, label = None, code
        self.code = code
        self.params = params
        self.label = label
        self.indent = indent

    def __str__(self):
        line = ''
        if self.label:
            if self.indent:
                line += self.indent[2:]
            line += f'{self.label}:'
            if self.code:
                line += ' '
        else:
            if self.indent:
                line += self.indent
        if self.code:
            line += self.code
            for p in self.params:
                line += ' ' + str(p)
        return line


def find_vars_decls(node: AstNode) -> List[VarsNode]:
    vars_nodes: List[VarsNode] = []

    def find(node: AstNode) -> None:
        for n in (node.childs or []):
            if isinstance(n, VarsNode):
                vars_nodes.append(n)
            else:
                find(n)

    find(node)
    return vars_nodes


class CodeGenerator:
    def __init__(self):
        self.code_lines: List[CodeLine] = []
        self.indent = ''

    def add(self, code: str, *params: Union[str, int, CodeLabel], label: CodeLabel = None):
        if isinstance(code, CodeLabel):
            code, label = None, code
        if code and len(code) > 0 and code[-1] == '}':
            self.indent = self.indent[2:]
        self.code_lines.append(CodeLine(code, *params, label=label, indent=self.indent))
        if code and len(code) > 0 and code[-1] == '{':
            self.indent = self.indent + '  '

    @property
    def code(self) -> [str, ...]:
        index = 0
        for cl in self.code_lines:
            line = cl.code
            if cl.label:
                cl.label.index = index
                index += 1
        code: List[str] = []
        for cl in self.code_lines:
            code.append(str(cl))
        return code
