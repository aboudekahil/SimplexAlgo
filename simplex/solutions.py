class SimplexNotFeasible:
    def __init__(self):
        self.msg = "Linear problem is not feasible"

    def __str__(self):
        return self.msg


# TODO fix naming
class SimplexSolutions:
    def __init__(self, *values: float):
        self.values = list(values)


SimplexSolution = SimplexNotFeasible | SimplexSolutions