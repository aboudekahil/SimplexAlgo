# TODO fix solution schema, probably make it one class that has an enum that indicates the type of solution and
# TODO attributes that give value
from fractions import Fraction


class Solutions:
    def __init__(self):
        self.values = {}
        self.msg = ""


class NotFeasible(Solutions, Exception):
    """
    Indicates that the simplex solution is not feasible
    """

    def __init__(self, msg="Linear problem is not feasible"):
        super(NotFeasible, self).__init__()

        self.msg = msg

    def __str__(self):
        return self.msg

class Solution(Solutions):
    def __init__(self, values: dict[str, Fraction]):
        """
        Solution constructor
        :param values: the z value
        """
        super().__init__()
        self.values = values

    def __str__(self) -> str:
        return self.values.__str__()

    def __repr__(self):
        return self.__str__()


class NotBounded(Solutions, Exception):
    def __init__(self):
        super(NotBounded, self).__init__()
        self.msg = "Linear problem is unbounded"

    def __str__(self):
        return self.msg

    def __repr__(self):
        return self.__str__()


class MultipleSolutions(Solutions, Exception):
    def __init__(self):
        super(MultipleSolutions, self).__init__()
        self.msg = "Linear problem contains multiple solutions"