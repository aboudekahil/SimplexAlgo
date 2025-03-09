from enum import Enum
from typing import Iterable, Self

class SimplexOperators(Enum):
    EQUAL = 1
    LESS_THAN_OR_EQUAL = 2
    GREATER_THAN_OR_EQUAL = 3

class SimplexMaxOrMin(Enum):
    MAX = 1
    MIN = 2

class SimplexFunction:
    def __init__(self, *args: Iterable[float], operator: SimplexOperators, constant: float):
        pass

class Simplex:
    def __init__(self):
        pass

class SimplexBuilder:
    def __init__(self, operation: SimplexMaxOrMin):
        pass

    def add_constraint(self) -> Self:
        return self

    def build(self) -> Simplex:
        pass




if __name__ == "__main__":
    pass