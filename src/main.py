from enum import Enum
from typing import Self

class SimplexOperators(Enum):
    EQUAL = 1
    LESS_THAN_OR_EQUAL = 2
    GREATER_THAN_OR_EQUAL = 3

class SimplexMaxOrMin(Enum):
    MAX = 1
    MIN = 2

class SimplexObjectiveFunction:
    def __init__(self, min_or_max: SimplexMaxOrMin, *args: float):
        pass

class SimplexConstraintFunction:
    def __init__(self, operator: SimplexOperators, *args: float):
        pass

class Simplex:
    def __init__(self, objective_function: SimplexObjectiveFunction, *args: SimplexConstraintFunction):
        pass

    def solve(self):
        pass

class SimplexBuilder:
    def __init__(self, objective_function: SimplexObjectiveFunction):
        pass

    def add_constraint(self, constraint: SimplexConstraintFunction) -> Self:
        return self

    def build(self) -> Simplex:
        pass




if __name__ == "__main__":
    a = SimplexConstraintFunction(SimplexOperators.EQUAL,1.0, 10.2)