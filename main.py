from simplex import *
from simplex.graphical_solution import solve_graphically

if __name__ == "__main__":
    #Objective function coefficient max c_x.x + c_y.y
    c_x = 4
    c_y = -7
    # Constraints coefficients a1.x + a2.y <= b1
    a1 = 5
    a2 = 1
    b1 = 15
    # Constraints coefficients c1.x + c2.y <= b2
    c1 = 2
    c2 = -2
    b2 = 7
    
    # Define the problem
    simplex: Simplex = (SimplexBuilder()
                        .set_number_of_vars(2,
                                            VariableDomains.GEQ_THAN_ZERO,
                                            VariableDomains.GEQ_THAN_ZERO)
                        .set_objective_function(ObjectiveFunction(MaxOrMin.MAX, c_x, c_y, 0))
                        .add_constraint(ConstraintFunction(Operators.LEQ, a1, a2, b1))
                        .add_constraint(ConstraintFunction(Operators.EQUAL, c1, c2, b2))
                        .set_to_standard_form()
                        .build())

    # Ask the user to choose the solving method
    method = input("Choose solving method (simplex/graphical): ").strip().lower()

    if method == "simplex":
        # Solve using the Simplex algorithm
        answer = simplex.solve()
        print(answer)
        if answer.__class__ != NotFeasible:
            print(answer.values)
    elif method == "graphical":
        # Solve graphically
        solve_graphically(
            objective=(c_x, c_y),  # Coefficients of the objective function
            constraints=[
                (a1, a2, b1),  # Coefficients and RHS of the first constraint
                (c1, c2, b2)    # Coefficients and RHS of the second constraint
            ]
        )
    else:
        print("Invalid method selected. Please choose either 'simplex' or 'graphical'.")
