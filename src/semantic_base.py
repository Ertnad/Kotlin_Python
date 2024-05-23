from typing import Any, Dict, Optional, Tuple
from enum import Enum


# по идее, должен быть описан в ast, но возникают проблемы с cross импортом модулей, с которыми пока лень разбираться
class BinOp(Enum):
    """Перечисление возможных биранных операций
    """

    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'
    MOD = '%'
    GT = '>'
    LT = '<'
    GE = '>='
    LE = '<='
    EQUALS = '=='
    NEQUALS = '!='
    BIT_AND = '&'
    BIT_OR = '|'
    LOGICAL_AND = '&&'
    LOGICAL_OR = '||'

    def __str__(self):
        return self.value


class UnOp(Enum):
    NOT = '!'

    def __str__(self):
        return self.value


class InOp(Enum):
    IN = 'in'

    def __str__(self):
        return self.value


class BaseType(Enum):
    """Перечисление для базовых типов данных
    """

    VOID = 'void'
    INT = 'Int'
    FLOAT = 'Float'
    BOOL = 'Boolean'
    STR = 'String'

    def __str__(self):
        return self.value


VOID, INT, FLOAT, BOOL, STR = BaseType.VOID, BaseType.INT, BaseType.FLOAT, BaseType.BOOL, BaseType.STR


class TypeDesc:
    """Класс для описания типа данных.

       Сейчас поддерживаются только примитивные типы данных и функции.
       Для поддержки сложных типов (массивы и т.п.) должен быть рассширен
    """

    VOID: 'TypeDesc'
    INT: 'TypeDesc'
    FLOAT: 'TypeDesc'
    BOOL: 'TypeDesc'
    STR: 'TypeDesc'

    def __init__(self, base_type_: Optional[BaseType] = None,
                 return_type: Optional['TypeDesc'] = None, params: Optional[Tuple['TypeDesc']] = None) -> None:
        self.base_type = base_type_
        self.return_type = return_type
        self.params = params

    @property
    def func(self) -> bool:
        return self.return_type is not None

    @property
    def is_simple(self) -> bool:
        return not self.func

    # Проверка на равенство типов при сравнении
    def __eq__(self, other: 'TypeDesc'):
        # если относительно друг друга разные
        if self.func != other.func:
            return False
        if not self.func:  # если не функция, то проверяем, совпадают ли базовые типы
            return self.base_type == other.base_type
        else:  # если функция
            if self.return_type != other.return_type:  # совпадают ли возвращаемые типы
                return False
            if len(self.params) != len(other.params):  # совпадает ли количество параметров
                return False
            for i in range(len(self.params)):
                if self.params[i] != other.params[i]:  # рекурсивно проверяются параметры
                    return False
            return True

    #  получает 'TypeDesc' из базового типа по имени
    @staticmethod
    def from_base_type(base_type_: BaseType) -> 'TypeDesc':
        return getattr(TypeDesc, base_type_.name)

    #  получает 'TypeDesc' из строки
    @staticmethod
    def from_str(str_decl: str) -> 'TypeDesc':
        try:
            base_type_ = BaseType(str_decl)  # конструируем базовый тип
            return TypeDesc.from_base_type(base_type_)  # используем метод выше
        except:
            raise SemanticException('Неизвестный тип {}'.format(str_decl))

    #  представляем определение типа в виде строки
    def __str__(self) -> str:
        if not self.func:
            return str(self.base_type)
        else:
            res = str(self.return_type)
            res += ' ('
            for param in self.params:
                if res[-1] != '(':
                    res += ', '
                res += str(param)
            res += ')'
        return res


for base_type in BaseType:
    setattr(TypeDesc, base_type.name, TypeDesc(base_type))


class ScopeType(Enum):
    """Перечисление для "области" декларации переменных
    """

    GLOBAL = 'global'
    #  наверное не нужно нам, только если язык позволяет писать вне функций
    GLOBAL_LOCAL = 'global.local'  # переменные относятся к глобальной области, но описаны в скобках (теряем имена)
    PARAM = 'param'
    LOCAL = 'local'

    def __str__(self):
        return self.value


class IdentDesc:
    """Класс для описания переменых
    """

    def __init__(self, name: str, type_: TypeDesc, scope: ScopeType = ScopeType.GLOBAL, index: int = 0) -> None:
        self.name = name
        self.type = type_
        self.scope = scope
        self.index = index
        self.built_in = False  # встроенная функция в язык программирования

    def __str__(self) -> str:
        return '{}, {}, {}'.format(self.type, self.scope, 'built-in' if self.built_in else self.index)


class IdentScope:
    """Класс для представлений областей видимости переменных во время семантического анализа
    """

    def __init__(self, parent: Optional['IdentScope'] = None) -> None:
        self.idents: Dict[str, IdentDesc] = {}  # Словарь идентификаторов
        self.func: Optional[IdentDesc] = None  # для переменных в функции
        self.parent = parent  # ссылка на родительскую область видимости
        self.var_index = 0  # подсчет
        self.param_index = 0

    @property
    def is_global(self) -> bool:
        return self.parent is None

    @property
    def curr_global(self) -> 'IdentScope':
        curr = self
        while curr.parent:
            curr = curr.parent
        return curr

    @property
    def curr_func(self) -> Optional['IdentScope']:
        curr = self
        while curr and not curr.func:
            curr = curr.parent
        return curr

    def add_ident(self, ident: IdentDesc) -> IdentDesc:
        func_scope = self.curr_func
        global_scope = self.curr_global

        if ident.scope != ScopeType.PARAM:
            ident.scope = ScopeType.LOCAL if func_scope else \
                ScopeType.GLOBAL if self == global_scope else ScopeType.GLOBAL_LOCAL

        old_ident = self.get_ident(ident.name)
        if old_ident:  # объявленный идентификатор уже есть в области видимости (текущей или вышестоящей)
            error = False
            if ident.scope == ScopeType.PARAM:  # если добавляемый идентификатор является параметром
                if old_ident.scope == ScopeType.PARAM:  # найденный тоже параметр
                    error = True
            elif ident.scope == ScopeType.LOCAL:  # если добавляется локальная переменная
                if old_ident.scope not in (ScopeType.GLOBAL, ScopeType.GLOBAL_LOCAL):  # найденная не была глобальной или глобально-локальной
                    error = True
            else:  # пытаемся объявить глобальную/глобально-локальную переменную, а такая уже есть
                error = True
            if error:
                raise SemanticException('Идентификатор {} уже объявлен'.format(ident.name))

        if not ident.type.func:
            if ident.scope == ScopeType.PARAM:
                ident.index = func_scope.param_index
                func_scope.param_index += 1
            else:
                ident_scope = func_scope if func_scope else global_scope
                ident.index = ident_scope.var_index
                ident_scope.var_index += 1

        self.idents[ident.name] = ident
        return ident

    def get_ident(self, name: str) -> Optional[IdentDesc]:
        scope = self
        ident = None
        while scope:
            ident = scope.idents.get(name)
            if ident:
                break
            scope = scope.parent
        return ident


class SemanticException(Exception):
    """Класс для исключений во время семантического анализа
    """

    def __init__(self, message, row: int = None, col: int = None, **kwargs: Any) -> None:
        if row or col:
            message += " ("
            if row:
                message += 'строка: {}'.format(row)
                if col:
                    message += ', '
            if row:
                message += 'позиция: {}'.format(col)
            message += ")"
        self.message = message


#  что к чему может быть приведено
TYPE_CONVERTIBILITY = {
    INT: (FLOAT, BOOL, STR),
    FLOAT: (STR,),
    BOOL: (STR,)
}


def can_type_convert_to(from_type: TypeDesc, to_type: TypeDesc) -> bool:
    if not from_type.is_simple or not to_type.is_simple:
        return False  # если какой-то тип не является простым
    return from_type.base_type in TYPE_CONVERTIBILITY and to_type.base_type in TYPE_CONVERTIBILITY[to_type.base_type]


BIN_OP_TYPE_COMPATIBILITY = {
    BinOp.ADD: {
        (INT, INT): INT,
        (FLOAT, FLOAT): FLOAT,
        (STR, STR): STR
    },
    BinOp.SUB: {
        (INT, INT): INT,
        (FLOAT, FLOAT): FLOAT
    },
    BinOp.MUL: {
        (INT, INT): INT,
        (FLOAT, FLOAT): FLOAT
    },
    BinOp.DIV: {
        (INT, INT): INT,
        (FLOAT, FLOAT): FLOAT
    },
    BinOp.MOD: {
        (INT, INT): INT,
        (FLOAT, FLOAT): FLOAT
    },
    BinOp.GT: {
        (INT, INT): BOOL,
        (FLOAT, FLOAT): BOOL,
        (STR, STR): BOOL,
    },
    BinOp.LT: {
        (INT, INT): BOOL,
        (FLOAT, FLOAT): BOOL,
        (STR, STR): BOOL,
    },
    BinOp.GE: {
        (INT, INT): BOOL,
        (FLOAT, FLOAT): BOOL,
        (STR, STR): BOOL,
    },
    BinOp.LE: {
        (INT, INT): BOOL,
        (FLOAT, FLOAT): BOOL,
        (STR, STR): BOOL,
    },
    BinOp.EQUALS: {
        (INT, INT): BOOL,
        (FLOAT, FLOAT): BOOL,
        (STR, STR): BOOL,
        (BOOL, BOOL): BOOL,
    },
    BinOp.NEQUALS: {
        (INT, INT): BOOL,
        (FLOAT, FLOAT): BOOL,
        (STR, STR): BOOL,
        (BOOL, BOOL): BOOL,
    },

    BinOp.BIT_AND: {
        (INT, INT): INT,
    },
    BinOp.BIT_OR: {
        (INT, INT): INT,
    },

    BinOp.LOGICAL_AND: {
        (BOOL, BOOL): BOOL,
    },
    BinOp.LOGICAL_OR: {
        (BOOL, BOOL): BOOL,
    },
}

UN_OP_TYPE_COMPATIBILITY = {
    UnOp.NOT: {
        BOOL: BOOL
    },
}

IN_OP_TYPE_COMPATIBILITY = {
    InOp.IN: {
        (INT, INT): BOOL,
        (FLOAT, FLOAT): BOOL,
        (STR, STR): BOOL,
        (BOOL, BOOL): BOOL,
    }
}
