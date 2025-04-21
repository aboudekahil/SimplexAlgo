import tkinter as tk
from tkinter import messagebox
from simplex import *
from simplex.graphical_solution import solve_graphically

class SimplexGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simplex Solver")

        self.var_entries = []
        self.constraint_entries = []

        # Objective function type (MAX or MIN)
        tk.Label(root, text="Objective Function Type:").grid(row=0, column=0, sticky="w")
        self.obj_type = tk.StringVar(value="MAX")  # Default to MAX
        obj_type_menu = tk.OptionMenu(root, self.obj_type, "MAX", "MIN")
        obj_type_menu.grid(row=0, column=1, sticky="w")

        # Objective function section
        tk.Label(root, text="Objective Function: Z = ").grid(row=1, column=0, sticky="w")
        self.obj_frame = tk.Frame(root)
        self.obj_frame.grid(row=2, column=0, columnspan=3, sticky="w")
        self.add_variable_entry()

        btn_add_var = tk.Button(root, text="+", command=self.add_variable_entry)
        btn_add_var.grid(row=2, column=3, sticky="w")

        # Constraints section
        tk.Label(root, text="Constraints:").grid(row=3, column=0, sticky="w")
        self.constr_frame = tk.Frame(root)
        self.constr_frame.grid(row=4, column=0, columnspan=4, sticky="w")

        # Remove the initial call to add_constraint_entry
        # Constraints will only be added when the user presses the "+" button
        btn_add_constr = tk.Button(root, text="+", command=self.add_constraint_entry)
        btn_add_constr.grid(row=4, column=4, sticky="w")

        # Buttons
        btn_simplex = tk.Button(root, text="Solve with Simplex", command=self.solve_simplex)
        btn_simplex.grid(row=99, column=0, pady=10)
        btn_graphical = tk.Button(root, text="Solve Graphically", command=self.solve_graphical)
        btn_graphical.grid(row=99, column=1, pady=10)
        btn_reset = tk.Button(root, text="Reset", command=self.reset)
        btn_reset.grid(row=99, column=2, pady=10)

    def add_variable_entry(self):
        col = len(self.var_entries)
        entry = tk.Entry(self.obj_frame, width=5)
        entry.grid(row=0, column=col*2)
        tk.Label(self.obj_frame, text=f"x{col+1}").grid(row=0, column=col*2+1)
        self.var_entries.append(entry)

    def add_constraint_entry(self):
        row = len(self.constraint_entries)
        frame = tk.Frame(self.constr_frame)
        frame.grid(row=row, column=0, sticky="w")
        entries = []

        # Add variable coefficients
        for i in range(len(self.var_entries)):
            e = tk.Entry(frame, width=5)
            e.grid(row=0, column=i*2)
            tk.Label(frame, text=f"x{i+1} +").grid(row=0, column=i*2+1)
            entries.append(e)

        # Add dropdown for constraint type (<=, >=, =)
        constraint_type = tk.StringVar(value="<=")  # Default to <=
        constraint_menu = tk.OptionMenu(frame, constraint_type, "<=", ">=", "=")
        constraint_menu.grid(row=0, column=len(self.var_entries)*2)
        entries.append(constraint_type)

        # Add RHS entry
        rhs = tk.Entry(frame, width=5)
        rhs.grid(row=0, column=len(self.var_entries)*2+1)
        entries.append(rhs)

        self.constraint_entries.append(entries)

    def reset(self):
        # Clear variable entries
        for entry in self.var_entries:
            entry.destroy()
        self.var_entries.clear()
        for widget in self.obj_frame.winfo_children():
            widget.destroy()
        self.add_variable_entry()

        # Clear constraint entries
        for entries in self.constraint_entries:
            for entry in entries:
                # Only destroy widgets (not StringVar objects)
                if isinstance(entry, tk.Widget):
                    entry.destroy()
        self.constraint_entries.clear()
        for widget in self.constr_frame.winfo_children():
            widget.destroy()

        # Reset objective function type
        self.obj_type.set("MAX")

    def solve_simplex(self):
        try:
            # Get objective function coefficients
            obj_coeffs = [float(entry.get()) for entry in self.var_entries]
            obj_type = self.obj_type.get()

            # Get constraints
            constraints = []
            for constraint in self.constraint_entries:
                coeffs = [float(entry.get()) for entry in constraint[:-2] if isinstance(entry, tk.Entry)]  # Coefficients
                constraint_type = constraint[-2].get()  # <=, >=, or =
                rhs = float(constraint[-1].get())  # RHS
                constraints.append((coeffs, constraint_type, rhs))

            # Build the simplex problem
            simplex = SimplexBuilder().set_number_of_vars(
                len(obj_coeffs),
                VariableDomains.GEQ_THAN_ZERO,
                VariableDomains.GEQ_THAN_ZERO
            ).set_objective_function(
                ObjectiveFunction(MaxOrMin.MAX if obj_type == "MAX" else MaxOrMin.MIN, *obj_coeffs, 0)
            )

            for coeffs, constraint_type, rhs in constraints:
                operator = Operators.LEQ if constraint_type == "<=" else Operators.GEQ if constraint_type == ">=" else Operators.EQ
                simplex.add_constraint(ConstraintFunction(operator, *coeffs, rhs))

            simplex = simplex.set_to_standard_form().build()

            # Solve the problem
            answer = simplex.solve()
            if answer.__class__ != NotFeasible:
                messagebox.showinfo("Simplex Solution", f"Optimal Solution: {answer.values}")
            else:
                messagebox.showerror("Simplex Solution", "The problem is not feasible.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def solve_graphical(self):
        try:
            # Get objective function coefficients
            obj_coeffs = [float(entry.get()) for entry in self.var_entries]
            obj_type = self.obj_type.get()

            # Get constraints
            constraints = []
            for constraint in self.constraint_entries:
                coeffs = [float(entry.get()) for entry in constraint[:-2]]  # Coefficients
                constraint_type = constraint[-2].get()  # <=, >=, or =
                rhs = float(constraint[-1].get())  # RHS
                constraints.append((*coeffs, rhs, constraint_type))

            # Solve graphically
            solve_graphically(
                objective=tuple(obj_coeffs),
                constraints=constraints,
                maximize=(obj_type == "MAX")
            )
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimplexGUI(root)
    root.mainloop()