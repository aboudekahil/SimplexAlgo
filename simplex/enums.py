from enum import Enum, auto, unique

@unique
class SimplexVariableDomains(Enum):
    LESS_THAN_ZERO = auto()
    GREATER_THAN_ZERO = auto()
    UNRESTRICTED = auto()


@unique
class SimplexOperators(Enum):
    EQUAL = auto()
    LESS_THAN_OR_EQUAL = auto()
    GREATER_THAN_OR_EQUAL = auto()


@unique
class SimplexMaxOrMin(Enum):
    MAX = auto()
    MIN = auto()