class SimplexError(Exception):
    """Base class for all custom Simplex errors"""
    pass

class SimplexInfeasibleError(SimplexError):
    """Error raised when the simplex algorithm is not feasible"""
    def __init__(self):
        super().__init__("Linear problem is infeasible")

class SimplexMultipleSolutionsError(SimplexError):
    """Error raised when the simplex algorithm has multiple optimal solutions"""
    def __init__(self):
        super().__init__("Linear problem has multiple optimal solutions")


class SimplexDegeneracyError(SimplexError):
    """Error raised when the simplex algorithm encounters degeneracy"""
    def __init__(self):
        super().__init__("Linear problem has degenerate basic solutions")


class SimplexUnboundedError(SimplexError):
    """Error raised when the simplex algorithm encounters an unbounded problem"""
    def __init__(self):
        super().__init__("Linear problem is unbounded")


class SimplexCyclicError(SimplexError):
    """Error raised when the simplex algorithm enters a cycle"""
    def __init__(self):
        super().__init__("Linear problem exhibits cycling")


class SimplexInvalidInputError(SimplexError):
    """Error raised when the simplex algorithm receives invalid input"""
    def __init__(self, message="Invalid input for simplex algorithm"):
        super().__init__(message)