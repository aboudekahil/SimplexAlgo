from enum import Enum
from typing import Self
from abc import ABC

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
        self.is_solved = False
        self.original_matrix = [[]]

    def solve(self):
        pass

class SimplexBuilder:
    def __init__(self):
        self.objective_function = None
        self.constraints = []
        self.num_vars = -1


    def add_constraint(self, constraint: SimplexConstraintFunction) -> Self:
        self.constraints.append(constraint)
        return self

    def build(self) -> Simplex:
        if self.objective_function is None:
            raise ValueError("Objective function for simplex not provided")

        if len(self.constraints) == 0:
            raise ValueError("No constraints provided")

        if self.num_vars <= 0:
            raise ValueError("No variables")

        return Simplex(self.objective_function, *self.constraints)




if __name__ == "__main__":
    a = SimplexConstraintFunction(SimplexOperators.EQUAL,1.0, 10.2)