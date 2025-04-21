import unittest
from fractions import Fraction
from simplex import (
    Simplex, SimplexBuilder, ObjectiveFunction, ConstraintFunction, 
    MaxOrMin, Operators, VariableDomains, NotFeasible, Solution
)
from simplex.exceptions import (
    SimplexError, SimplexMultipleSolutionsError, SimplexUnboundedError, SimplexInfeasibleError,
    SimplexDegeneracyError, SimplexCyclicError, SimplexInvalidInputError
)

class TestSimplexSolver(unittest.TestCase):
    def test_multiple_optimal_solutions(self):
        """Test that the simplex algorithm correctly identifies problems with multiple optimal solutions"""
        simplex = (SimplexBuilder()
            .set_number_of_vars(2,
                                VariableDomains.GEQ_THAN_ZERO,
                                VariableDomains.GEQ_THAN_ZERO)
            .set_objective_function(ObjectiveFunction(MaxOrMin.MAX, 1, 1, 0))
            .add_constraint(ConstraintFunction(Operators.LEQ, 1, 1, 4))   # x1 + x2 ≤ 4
            .add_constraint(ConstraintFunction(Operators.LEQ, 1, 0, 2))   # x1 ≤ 2
            .add_constraint(ConstraintFunction(Operators.LEQ, 0, 1, 2))   # x2 ≤ 2
            .set_to_standard_form()
            .build())

        with self.assertRaises(SimplexMultipleSolutionsError):
            simplex.solve()

    
    def test_infeasible_problem(self):
        """Test that the simplex algorithm correctly identifies when there's no feasible solution"""
        simplex = (SimplexBuilder()
                  .set_number_of_vars(2,
                                    VariableDomains.GEQ_THAN_ZERO,
                                    VariableDomains.GEQ_THAN_ZERO)
                  .set_objective_function(ObjectiveFunction(MaxOrMin.MAX, 1, 1, 0))
                  .add_constraint(ConstraintFunction(Operators.GEQ, 1, 1, 10))
                  # These two constraints are inconsistent, making the problem infeasible
                  .add_constraint(ConstraintFunction(Operators.LEQ, 1, 0, 3))
                  .add_constraint(ConstraintFunction(Operators.GEQ, 1, 0, 6))
                  .set_to_standard_form()
                  .build())
        
        with self.assertRaises(SimplexInfeasibleError):
            simplex.solve()

    def test_unbounded_problem(self):
        """Test that the simplex algorithm correctly identifies unbounded solutions"""
        simplex = (SimplexBuilder()
                  .set_number_of_vars(2,
                                    VariableDomains.GEQ_THAN_ZERO,
                                    VariableDomains.GEQ_THAN_ZERO)
                  .set_objective_function(ObjectiveFunction(MaxOrMin.MAX, 1, 1, 0))
                  # No upper bounds, problem is unbounded
                  .add_constraint(ConstraintFunction(Operators.GEQ, 1, 0, 0))
                  .add_constraint(ConstraintFunction(Operators.GEQ, 0, 1, 0))
                  .set_to_standard_form()
                  .build())
        
        with self.assertRaises(SimplexUnboundedError):
            simplex.solve()

    def test_degenerate_problem(self):
        """Test that the simplex algorithm correctly identifies degenerate problems"""
        simplex = (SimplexBuilder()
                  .set_number_of_vars(2,
                                    VariableDomains.GEQ_THAN_ZERO,
                                    VariableDomains.GEQ_THAN_ZERO)
                  .set_objective_function(ObjectiveFunction(MaxOrMin.MAX, 2, 1, 0))
                  .add_constraint(ConstraintFunction(Operators.LEQ, 1, 1, 1))
                  .add_constraint(ConstraintFunction(Operators.LEQ, 1, 0, 0.5))
                  .add_constraint(ConstraintFunction(Operators.LEQ, 0, 1, 0.5))
                  .set_to_standard_form()
                  .build())
        
        with self.assertRaises(SimplexDegeneracyError):
            simplex.solve()
    
    def test_cycling_problem(self):
        """Test that the simplex algorithm correctly identifies cycling problems"""
        # This is a well-known cycling example (Beale's example)
        # Create a problem prone to cycling
        # This is a simplified version; real cycling problems are complex
        simplex = (SimplexBuilder()
                  .set_number_of_vars(3,
                                    VariableDomains.GEQ_THAN_ZERO,
                                    VariableDomains.GEQ_THAN_ZERO,
                                    VariableDomains.GEQ_THAN_ZERO)
                  .set_objective_function(ObjectiveFunction(MaxOrMin.MAX, -1, -1, -1, 0))
                  .add_constraint(ConstraintFunction(Operators.LEQ, 1/4, 1, -1, 1))
                  .add_constraint(ConstraintFunction(Operators.LEQ, 1, -1, 1, 2))
                  .add_constraint(ConstraintFunction(Operators.LEQ, -1, 1, 1, 2))
                  .set_to_standard_form()
                  .build())
        
        with self.assertRaises(SimplexCyclicError):
            simplex.solve()
    
    def test_regular_solution(self):
        """Test a normal problem with a unique, bounded solution"""
        simplex = (SimplexBuilder()
                  .set_number_of_vars(2,
                                    VariableDomains.GEQ_THAN_ZERO,
                                    VariableDomains.GEQ_THAN_ZERO)
                  .set_objective_function(ObjectiveFunction(MaxOrMin.MAX, 40, 80, 0))
                  .add_constraint(ConstraintFunction(Operators.LEQ, 2, 3, 48))
                  .add_constraint(ConstraintFunction(Operators.LEQ, 1, 0, 15))
                  .add_constraint(ConstraintFunction(Operators.LEQ, 0, 1, 10))
                  .set_to_standard_form()
                  .build())
        
        solution = simplex.solve()
        self.assertIsInstance(solution, Solution)
        self.assertAlmostEqual(solution.values['z'], 1160.0, places=5)
        self.assertAlmostEqual(solution.values.get('x0', 0), 9.0, places=5)  # x1 = 3
        self.assertAlmostEqual(solution.values.get('s-2', 0), 10.0, places=5)  # x2 = 2


if __name__ == "__main__":
    unittest.main()