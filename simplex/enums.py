from enum import Enum, auto, unique
from typing import Self


@unique
class VariableDomains(Enum):
    """
    VariableDomains is used for specifying the domains of the variables used in the simplex.
    """
    LEQ_THAN_ZERO = auto()
    """
    Specifies that a variable x is less than or equal to 0.
    """

    GEQ_THAN_ZERO = auto()
    """
    Specifies that a variable x is greater than or equal to 0.
    """

    UNRESTRICTED = auto()
    """
    Specifies that a variable x can be any real number.
    """


@unique
class Operators(Enum):
    """
    Operators to be used in simplex constraint equations.
    """

    EQUAL = auto()
    """
    Corresponds to an equation where Ax = b.
    """

    LEQ = auto()
    """
    Corresponds to an inequality where Ax <= b.
    """

    GEQ = auto()
    """
    Corresponds to an inequality where Ax >= b.
    """


@unique
class MaxOrMin(Enum):
    """
    Max or Min operators on the objective function z.
    """

    MAX = auto()
    """
    Corresponds to when you're trying to max an equation.
    """

    MIN = auto()
    """
    Corresponds to when you're trying to min an equation.
    """

    @classmethod
    def from_text(cls, text: str) -> Self:
        text = text.strip()
        match text.lower():
            case "min":
                return MaxOrMin.MIN
            case "max":
                return MaxOrMin.MAX
            case _:
                raise ValueError("Inputted parameter is neither max nor min")
