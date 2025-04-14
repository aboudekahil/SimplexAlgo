from simplex import *

if __name__ == "__main__":
    simplex: Simplex = (SimplexBuilder()
                        .set_number_of_vars(2,
                                            VariableDomains.GEQ_THAN_ZERO,
                                            VariableDomains.GEQ_THAN_ZERO)
                        .set_objective_function(ObjectiveFunction(MaxOrMin.MAX, 1, 1, 0))
                        .add_constraint(ConstraintFunction(Operators.LEQ, 1, 2, 24))
                        .add_constraint(ConstraintFunction(Operators.EQUAL, 1, 0, 2))
                        .set_to_standard_form()
                        .build())

    answer = simplex.solve()
    print(answer)
    if answer.__class__ != NotFeasible:
        print(answer.values)
