import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        from simplex import (Simplex,
                             SimplexBuilder,
                             VariableDomains,
                             ObjectiveFunction,
                             ConstraintFunction,
                             Operators,
                             MaxOrMin)

        simplex: Simplex = (SimplexBuilder()
                            .set_number_of_vars(2,
                                                VariableDomains.GREATER_THAN_ZERO,
                                                VariableDomains.GREATER_THAN_ZERO)
                            .set_objective_function(ObjectiveFunction(MaxOrMin.MAX, 1, 1, 0))
                            .add_constraint(ConstraintFunction(Operators.LESS_THAN_OR_EQUAL, 1, 2, 24))
                            .add_constraint(ConstraintFunction(Operators.EQUAL, 1, 0, 2))
                            .set_to_standard_form()
                            .build())

        answer = simplex.solve()

        self.assertEqual(answer.values, [13])


if __name__ == '__main__':
    unittest.main()
