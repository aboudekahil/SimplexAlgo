from simplex import *

if __name__ == "__main__":
    simplex: Simplex = (SimplexBuilder()
                        .set_number_of_vars(2,
                        SimplexVariableDomains.GREATER_THAN_ZERO,
                        SimplexVariableDomains.GREATER_THAN_ZERO)
                        .set_objective_function(SimplexObjectiveFunction(SimplexMaxOrMin.MAX, 1, 1, 0))
                        .add_constraint(SimplexConstraintFunction(SimplexOperators.LESS_THAN_OR_EQUAL, 1, 2, 24))
                        .add_constraint(SimplexConstraintFunction(SimplexOperators.EQUAL, 1, 0, 2))
                        .set_to_standard_form()
                        .build())

    answer = simplex.solve()

    if answer.__class__ != SimplexNotFeasible:
        print(answer.values)
