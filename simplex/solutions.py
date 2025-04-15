# TODO fix solution schema, probably make it one class that has an enum that indicates the type of solution and
# TODO attributes that give value


class Solutions:
    def __init__(self, *values: float):
        self.values = []
        self.msg = ""

class NotFeasible(Solutions, Exception):
    """
    Indicates that the simplex solution is not feasible
    """
    def __init__(self):
        super().__init__()
        self.msg = "Linear problem is not feasible"

    def __str__(self):
        return self.msg


# TODO fix naming
class Solution(Solutions):
    def __init__(self, *values: float):
        """
        Solution constructor
        :param values: the z value
        """
        super().__init__()
        self.values = list(values)


class NotBounded(Solutions, Exception):
    def __init__(self):
        super().__init__()
        self.msg = "Linear problem is unbounded"

    def __str__(self):
        return self.msg
