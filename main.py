from simplex import *
from simplex.graphical_solution import solve_graphically

if __name__ == "__main__":
    # For graphical solution
    maximize = False  # Set to False for minimization

    # Objective function coefficients: min z = 3x1 + 2x2
    c_x = 3
    c_y = 2

    # Constraints
    a1, a2, b1 = 5, 1, 10  # 5x1 + x2 >= 10
    c1, c2, b2 = 1, 1, 6   # x1 + x2 >= 6
    d1, d2, b3 = 1, 4, 12  # x1 + 4x2 >= 12

    # Define the problem
    simplex: Simplex = (SimplexBuilder()
                        .set_number_of_vars(2,
                                            VariableDomains.GEQ_THAN_ZERO,
                                            VariableDomains.GEQ_THAN_ZERO)
                        .set_objective_function(ObjectiveFunction(MaxOrMin.MIN, c_x, c_y, 0))
                        .add_constraint(ConstraintFunction(Operators.GEQ, a1, a2, b1))
                        .add_constraint(ConstraintFunction(Operators.GEQ, c1, c2, b2))
                        .add_constraint(ConstraintFunction(Operators.GEQ, d1, d2, b3))
                        .set_to_standard_form()
                        .build())

    # Ask the user to choose the solving method
    method = input("Choose solving method (simplex/graphical): ").strip().lower()

    if method == "simplex":
        # Solve using the Simplex algorithm
        answer = simplex.solve()
        if answer.__class__ != NotFeasible:
            print(answer.values)
        else:
            print("The problem is not feasible.")
    elif method == "graphical":
        # Solve graphically
        solve_graphically(
            objective=(c_x, c_y),  # Coefficients of the objective function
            constraints=[
                (a1, a2, b1, ">="),  # Coefficients and RHS of the first constraint
                (c1, c2, b2, ">="),  # Coefficients and RHS of the second constraint
                (d1, d2, b3, ">=")   # Coefficients and RHS of the third constraint
            ],
            maximize=maximize  # Set to True for maximization, False for minimization
        )
    else:
        print("Invalid method selected. Please choose either 'simplex' or 'graphical'.")
