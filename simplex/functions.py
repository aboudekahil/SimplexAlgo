from abc import ABC, abstractmethod
from simplex.enums import SimplexMaxOrMin, SimplexOperators


class SimplexFunction(ABC):
    @abstractmethod
    def num_vars(self):
        # TODO write not implemented error
        raise NotImplementedError()


class SimplexObjectiveFunction(SimplexFunction):
    def __init__(self, min_or_max: SimplexMaxOrMin, *args: float):
        self.operator = min_or_max
        self.values = list(args)

    @property
    def num_vars(self):
        return len(self.values) - 1

    def __str__(self):
        # TODO fix formatting
        str_rep = f"{'min' if self.operator == SimplexMaxOrMin.MIN else 'max'} z = "

        for indx, value in enumerate(self.values[:-1]):
            str_rep += f"({value}x{indx + 1}) + "

        str_rep += f"{self.values[-1]}"

        return str_rep


class SimplexConstraintFunction(SimplexFunction):
    def __init__(self, operator: SimplexOperators, *args: float):
        self.values = list(args)
        self.operator = operator

    @property
    def num_vars(self):
        return len(self.values) - 1

    def __str__(self):
        str_rep = "".join(
            map(lambda x: f"({x[1]}x{x[0] + 1}) + ", enumerate(self.values[:-2])))

        str_rep += f"({len(self.values) - 2}x{self.values[-2]})"

        match self.operator:
            case SimplexOperators.EQUAL:
                str_rep += f"  = {self.values[-1]}"
            case SimplexOperators.LESS_THAN_OR_EQUAL:
                str_rep += f" <= {self.values[-1]}"
            case SimplexOperators.GREATER_THAN_OR_EQUAL:
                str_rep += f" >= {self.values[-1]}"

        return str_rep
