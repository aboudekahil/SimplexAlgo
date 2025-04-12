# TODO fix solution schema, probably make it one class that has an enum that indicates the type of solution and
# TODO attributes that give value

class NotFeasible:
    """
    Indicates that the simplex solution is not feasible
    """
    def __init__(self):
        self.msg = "Linear problem is not feasible"

    def __str__(self):
        return self.msg


# TODO fix naming
class Solutions:
    def __init__(self, *values: float):
        """
        Solution constructor
        :param values: the z value
        """
        self.values = list(values)


Solution = NotFeasible | Solutions