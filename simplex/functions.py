from fractions import Fraction

from simplex.enums import MaxOrMin, Operators


class ObjectiveFunction:
    """
    The objective function to be used in the simplex.
    """

    def __init__(self, min_or_max: MaxOrMin, *args: Fraction):
        """
        Constructor for the objective function.
        :param min_or_max: Whether we want to minimize or maximize a function.
        :param args: The coefficients of the objective function with the last one being the right hand side.
        """
        self.operator = min_or_max
        self.values = list(map(Fraction, args))

    @property
    def num_vars(self):
        """
        :return: The number of variables used in the objective function.
        """
        return len(self.values) - 1

    def __str__(self):
        """
        :return: String representation of the objective function.
        """
        # TODO fix formatting
        str_rep = f"{'min' if self.operator == MaxOrMin.MIN else 'max'} z = "

        for indx, value in enumerate(self.values[:-2]):
            str_rep += f"({value})x{indx} + "

        if self.values[-1] != 0:
            str_rep += f"({self.values[-2]})x{len(self.values) - 2} + ({self.values[-1]})"
        else:
            str_rep += f"({self.values[-2]})x{len(self.values) - 2}"

        return str_rep


class ConstraintFunction:
    """
    The constraint function to be used in the simplex.
    """

    def __init__(self, operator: Operators, *args: Fraction):
        """
        Constraint function constructor
        :param operator: Operator used for which type of constraint it is.
        :param args: Coefficients of the constraint function with the last one being the right hand side.
        """
        self.values = list(map(Fraction, args))
        self.operator = operator

    @property
    def num_vars(self):
        """
        :return: The number of variables used in the objective function.
        """
        return len(self.values) - 1

    def __str__(self):
        """
        :return: String representation of the constraint function.
        """
        str_rep = ""

        for indx, val in enumerate(self.values[:-2]):
            str_rep += f"({val})x{indx} + "

        str_rep += f"({self.values[-2]})x{len(self.values) - 2}"

        match self.operator:
            case Operators.EQUAL:
                str_rep += f"  = {self.values[-1]}"
            case Operators.LEQ:
                str_rep += f" <= {self.values[-1]}"
            case Operators.GEQ:
                str_rep += f" >= {self.values[-1]}"

        return str_rep
