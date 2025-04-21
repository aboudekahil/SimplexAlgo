import tkinter as tk
from tkinter import messagebox
from simplex import *
from simplex.graphical_solution import solve_graphically

def solve_simplex():
    try:
        # Get input values
        c_x = float(entry_cx.get())
        c_y = float(entry_cy.get())
        a1 = float(entry_a1.get())
        a2 = float(entry_a2.get())
        b1 = float(entry_b1.get())
        c1 = float(entry_c1.get())
        c2 = float(entry_c2.get())
        b2 = float(entry_b2.get())

        # Define the problem
        simplex = (SimplexBuilder()
                   .set_number_of_vars(2,
                                       VariableDomains.GEQ_THAN_ZERO,
                                       VariableDomains.GEQ_THAN_ZERO)
                   .set_objective_function(ObjectiveFunction(MaxOrMin.MAX, c_x, c_y, 0))
                   .add_constraint(ConstraintFunction(Operators.LEQ, a1, a2, b1))
                   .add_constraint(ConstraintFunction(Operators.LEQ, c1, c2, b2))
                   .set_to_standard_form()
                   .build())

        # Solve using the Simplex algorithm
        answer = simplex.solve()
        if answer.__class__ == NotFeasible:
            messagebox.showinfo("Result", "The problem is not feasible.")
        else:
            messagebox.showinfo("Result", f"Optimal Solution: {answer.values}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def solve_graphical():
    try:
        # Get input values
        c_x = float(entry_cx.get())
        c_y = float(entry_cy.get())
        a1 = float(entry_a1.get())
        a2 = float(entry_a2.get())
        b1 = float(entry_b1.get())
        c1 = float(entry_c1.get())
        c2 = float(entry_c2.get())
        b2 = float(entry_b2.get())

        # Solve graphically
        solve_graphically(
            objective=(c_x, c_y),
            constraints=[
                (a1, a2, b1),
                (c1, c2, b2)
            ]
        )
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Create the main window
root = tk.Tk()
root.title("Simplex Solver")

# Objective function inputs
tk.Label(root, text="Objective Function: Max Z = c_x*x + c_y*y").grid(row=0, column=0, columnspan=2)
tk.Label(root, text="c_x:").grid(row=1, column=0)
entry_cx = tk.Entry(root)
entry_cx.grid(row=1, column=1)
tk.Label(root, text="c_y:").grid(row=2, column=0)
entry_cy = tk.Entry(root)
entry_cy.grid(row=2, column=1)

# Constraint 1 inputs
tk.Label(root, text="Constraint 1 (a1.x + a2.y <= b1):").grid(row=3, column=0, columnspan=2)
tk.Label(root, text="a1:").grid(row=4, column=0)
entry_a1 = tk.Entry(root)
entry_a1.grid(row=4, column=1)
tk.Label(root, text="a2:").grid(row=5, column=0)
entry_a2 = tk.Entry(root)
entry_a2.grid(row=5, column=1)
tk.Label(root, text="b1:").grid(row=6, column=0)
entry_b1 = tk.Entry(root)
entry_b1.grid(row=6, column=1)

# Constraint 2 inputs
tk.Label(root, text="Constraint 2 (c1.x + c2.y <= b2):").grid(row=7, column=0, columnspan=2)
tk.Label(root, text="c1:").grid(row=8, column=0)
entry_c1 = tk.Entry(root)
entry_c1.grid(row=8, column=1)
tk.Label(root, text="c2:").grid(row=9, column=0)
entry_c2 = tk.Entry(root)
entry_c2.grid(row=9, column=1)
tk.Label(root, text="b2:").grid(row=10, column=0)
entry_b2 = tk.Entry(root)
entry_b2.grid(row=10, column=1)

# Buttons
btn_simplex = tk.Button(root, text="Solve with Simplex", command=solve_simplex)
btn_simplex.grid(row=11, column=0, pady=10)
btn_graphical = tk.Button(root, text="Solve Graphically", command=solve_graphical)
btn_graphical.grid(row=11, column=1, pady=10)

# Run the application
root.mainloop()