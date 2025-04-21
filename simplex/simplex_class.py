from fractions import Fraction
from typing import Optional

from simplex import MaxOrMin, ObjectiveFunction, ConstraintFunction, Solution, NotFeasible, VariableDomains, Operators, NotBounded

from simplex.exceptions import (
    SimplexMultipleSolutionsError,
    SimplexUnboundedError,
    SimplexCyclicError,
    SimplexDegeneracyError,
    SimplexInfeasibleError
)

class Simplex:
    def __init__(self):
        """
        Simplex Constructor
        """
        self.__tableau: Optional[list[list[Fraction]]] = None
        self.__pivot = None
        self.num_vars: int = -1
        self.objective_function: Optional[ObjectiveFunction] = None
        self.constraints: Optional[list[ConstraintFunction]] = None
        self.domains = None
        self.number_of_slack_variables: int = 0
        self.was_min = False

    def solve(self) -> Solution:
        """
        Solves the simplex and returns the solution in the form of a simplex solution class.
        :return: The simplex solution
        """
        self.__tableau = self.__create_tableau()
        history = set()
        # Check for unbounded solution before anything else
        if self.__detect_unbounded_solution():
            raise SimplexUnboundedError()

        if self.__check_if_two_step():
            # Check for unbounded solution before first phase
            if self.__detect_unbounded_solution(use_aux=True):
                raise SimplexUnboundedError()
                
            self.__tableau = self.__solve_first_phase()

        while not self.__is_solved():
            # Check for unbounded solution
            if self.__detect_unbounded_solution():
                raise SimplexUnboundedError()
                
            # Check for cycling - add the current tableau state to history
            tableau_sig = self.__get_tableau_signature()
            if tableau_sig in history:
                raise SimplexCyclicError()
            history.add(tableau_sig)
                
            pivot = self.__find_pivot()
            if pivot[1] < 0:
                raise NotFeasible()

            self.__fix_pivot(pivot)
            

        # After finding a solution, check for multiple solutions
        if self.__detect_multiple_solutions():
            raise SimplexMultipleSolutionsError()
        
        # Check for degeneracy
        if self.__detect_degeneracy():
            raise SimplexDegeneracyError()

        return self.__get_solution()


    def __is_solved(self) -> bool:
        """
        Checks whether the simplex is solved yet or no.
        :return: boolean true if solved false otherwise.
        """
        is_solved = True

        for i, x in enumerate(self.__tableau[-1]):
            if x < 0 and i != len(self.__tableau[-1]) - 1:
                is_solved = False

        return is_solved

    def __find_pivot(self) -> tuple[int, int]:
        """
        Returns a tuple with the location of the pivot.
        :return: a tuple with the location of the pivot.
        """
        entering_indx = self.__get_entering_var()
        leaving_indx = self.__get_leaving_var(entering_indx)
        return entering_indx, leaving_indx

    def __fix_pivot(self, pivot_indx: tuple[int, int]):
        """
        Does row echelon operations to make the soon-to-be pivot an actual pivot.
        :param pivot_indx: The location of the pivot
        """
        j, i = pivot_indx

        pivot = self.__tableau[i][j]
        self.__tableau[i] = [element / pivot for element in self.__tableau[i]]

        for indx, row in enumerate(self.__tableau):
            if indx != i:
                row_scale = [y * self.__tableau[indx][j] for y in self.__tableau[i]]
                self.__tableau[indx] = [x - y for x, y in zip(self.__tableau[indx], row_scale)]

    def __get_solution(self) -> Solution:
        """
        Returns the solution of the simplex.
        :return: the solution of the simplex.
        """
        solution = {'z': self.__tableau[-1][-1]}

        for i, row in enumerate(self.__tableau[:-1]):
            for j, col in enumerate(self.__tableau[i]):
                if self.__tableau[i][j] == 1:
                    for i2, _ in enumerate(self.__tableau):
                        if i2 != i and self.__tableau[i2][j] != 0:
                            break
                    else:
                        if (j + 1) >= (self.num_vars - self.number_of_slack_variables):
                            solution[f"s{j - self.number_of_slack_variables}"] = row[-1]
                        else:
                            solution[f"x{j}"] = row[-1]

        if self.was_min:
            solution['z'] *= -1

        return Solution(solution)

    def __str__(self):
        """
        A string representation of the simplex.
        :return: A string representation of the simplex.
        """
        str_rep = f"""
{self.objective_function}
/
"""
        for constraint in self.constraints:
            str_rep += f"{constraint}\n"

        str_rep += "--------\n"

        for indx, domain in enumerate(self.domains):
            match domain:
                case VariableDomains.GEQ_THAN_ZERO:
                    str_rep += f"x{indx} >= 0\n"
                case VariableDomains.LEQ_THAN_ZERO:
                    str_rep += f"x{indx} <= 0\n"
                case VariableDomains.UNRESTRICTED:
                    str_rep += f"x{indx} in R\n"

        return str_rep

    def __create_tableau(self) -> list[list[Fraction]]:
        """
        Creates the simplex tableau
        :return: the simplex tableau
        """
        tableau = []
        slack_to_add: list[tuple[int, int]] = []
        artificial_to_add: list[int] = []
        for indx, constraint in enumerate(self.constraints):
            if constraint.operator == Operators.LEQ:
                slack_to_add.append((1, indx))
            elif constraint.operator == Operators.GEQ:
                slack_to_add.append((-1, indx))
                artificial_to_add.append(indx)
            else:
                artificial_to_add.append(indx)

        self.number_of_slack_variables = len(slack_to_add)

        for sign, indx in slack_to_add:
            self.__add_slack_variable(sign, indx)

        for indx in artificial_to_add:
            self.__add_artificial_variable(indx)

        for constraint in self.constraints:
            tableau.append(constraint.values)

        z_arr = list(map(lambda x: -x, self.objective_function.values[:-1])) + [self.objective_function.values[-1]]
        tableau.append(z_arr)

        if len(artificial_to_add) > 0:
            i_arr = [Fraction.from_float(0)] * (self.num_vars - len(artificial_to_add)) + (
                        [1] * len(artificial_to_add)) + [Fraction.from_float(0)]
            for indx in artificial_to_add:
                for indx2, val in enumerate(tableau[indx]):
                    i_arr[indx2] -= val
            tableau.append(i_arr)

        return tableau

    def __get_entering_var(self) -> int:
        """
        Returns indx of the variable to enter the basis
        :return: indx of the variable to enter the basis
        """
        z_arr = self.__tableau[-1]
        smallest_indx = 0
        smallest = z_arr[smallest_indx]

        for indx, val in enumerate(z_arr[:-1]):
            if val < smallest:
                smallest = val
                smallest_indx = indx

        return smallest_indx

    def __get_leaving_var(self, entering_indx) -> int:
        """
        Returns indx of the variable to leave the basis
        :return: indx of the variable to leave the basis
        :param entering_indx: indx of variable entering the basis
        :return: indx of the variable leaving the basis
        """
        skip = 0
        min_ratio_indx = -1
        min_ratio = 0

        for indx, x in enumerate(self.__tableau):
            if x[entering_indx] != 0 and x[-1] / x[entering_indx] > 0:
                skip = indx
                min_ratio_indx = indx
                min_ratio = x[-1] / x[entering_indx]
                break

        if min_ratio > 0:
            for indx, x in enumerate(self.__tableau):
                if indx > skip and x[entering_indx] > 0:
                    ratio = x[-1] / x[entering_indx]
                    if min_ratio > ratio:
                        min_ratio = ratio
                        min_ratio_indx = indx

        return min_ratio_indx

    def __add_slack_variable(self, sign: int, indx: int):
        """
        Adds slack variable to the problem.
        :param sign: -1 if constraint is >= 1 if <=
        :param indx: index of the slack variable in the constraints.
        """
        for i, constraint in enumerate(self.constraints):
            constraint.values.insert(len(constraint.values) - 1, sign if i == indx else 0)

        self.objective_function.values.insert(len(self.objective_function.values) - 1, 0)
        self.num_vars += 1

    def __add_artificial_variable(self, indx: int):
        """
        Adds artificial variables to the simplex
        :param indx: constraint index where we add the artificial variable.
        """
        for i, constraint in enumerate(self.constraints):
            constraint.values.insert(len(constraint.values) - 1, 1 if i == indx else 0)

        self.objective_function.values.insert(len(self.objective_function.values) - 1, 0)
        self.num_vars += 1

    def __check_if_two_step(self) -> bool:
        """
        checks if the simplex requires two steps to solve.
        :return: True if it needs two steps false otherwise.
        """
        for constraint in self.constraints:
            if constraint.operator == Operators.EQUAL or constraint.operator == Operators.GEQ:
                return True
        return False

    def __solve_first_phase(self) -> list[list[Fraction]]:
        """
        Solves the first phase in a two phase simplex.
        :return: the resulting tableau after the first phase.
        """
        number_of_artificial_variables = 0
        for constraint in self.constraints:
            if constraint.operator == Operators.EQUAL or constraint.operator == Operators.GEQ:
                number_of_artificial_variables += 1

        if number_of_artificial_variables == 0:
            return self.__tableau

        # Create a history set for the first phase
        first_phase_history = set()

        while not self.__is_solved():
            # Always check for unboundedness first - this is critical!
            if self.__detect_unbounded_solution(use_aux=True):
                raise SimplexUnboundedError()
                
            # Check for cycling
            tableau_sig = tuple(tuple(round(float(cell), 6) for cell in row) for row in self.__tableau)
            if tableau_sig in first_phase_history:
                raise SimplexCyclicError()
            first_phase_history.add(tableau_sig)

            pivot = self.__find_first_phase_pivot()
            if pivot[1] < 0:
                raise SimplexInfeasibleError()
                
            self.__fix_pivot(pivot)

        if self.__tableau[-1][-1] != 0:
            raise SimplexInfeasibleError()

        self.__tableau = self.__tableau[:-1]  # Remove auxiliary objective row

        for row in self.__tableau:
            for i in range(number_of_artificial_variables):
                row.pop(-2)

        return self.__tableau

    def __find_first_phase_pivot(self) -> tuple[int, int]:
        """
        Finds the pivot and returns its location in the first phase.
        :return: the index of the pivot in the tableau.
        """
        entering_indx = self.__get_entering_var()
        leaving_indx = self.__get_leaving_var_first_phase(entering_indx)
        return entering_indx, leaving_indx

    def __get_leaving_var_first_phase(self, entering_indx) -> int:
        """
        Gets the leaving basis variable in the first phase.
        :param entering_indx: the index of the variable entering the basis
        :return: the index of the variable leaving the basis
        """
        skip = 0
        min_ratio_indx = -1
        min_ratio = 0

        for indx, x in enumerate(self.__tableau[:-2]):
            if x[entering_indx] != 0 and x[-1] / x[entering_indx] > 0:
                skip = indx
                min_ratio_indx = indx
                min_ratio = x[-1] / x[entering_indx]
                break

        if min_ratio > 0:
            for indx, x in enumerate(self.__tableau[:-2]):
                if indx > skip and x[entering_indx] > 0:
                    ratio = x[-1] / x[entering_indx]
                    if min_ratio > ratio:
                        min_ratio = ratio
                        min_ratio_indx = indx

        return min_ratio_indx

    # --------------rabab-------------------

    def __get_tableau_signature(self):
        """
        Returns a hashable representation of the current tableau for cycle detection.
        """
        # Round values to avoid floating point issues and convert to tuple for hashability
        return tuple(tuple(round(float(cell), 6) for cell in row) for row in self.__tableau)


    def __detect_unbounded_solution(self, use_aux: bool = False) -> bool:
        """
        Check if the current tableau represents an unbounded problem.
        A maximization problem is unbounded if there is a negative entry in the objective row
        and all entries in that column in the constraint rows are non-positive.
        """
        if self.__tableau is None:
            return False
            
        last_row_index = len(self.__tableau) - 1
        if use_aux and len(self.__tableau) > 1:
            last_row_index = len(self.__tableau) - 2  # Use auxiliary objective row for phase 1
        
        z_row = self.__tableau[last_row_index]
        
        # For each non-basic variable (column)
        for col in range(len(z_row) - 1):  # skip RHS
            obj_coeff = z_row[col]
            
            # For maximization problems, we look for negative coefficients
            if obj_coeff < 0:
                # Check if all entries in the constraints are <= 0
                all_non_positive = True
                for row in range(last_row_index):  # Only check constraint rows
                    if self.__tableau[row][col] > 0:
                        all_non_positive = False
                        break
                
                if all_non_positive:
                    # Found a column with negative objective coefficient and all non-positive constraint coefficients
                    return True
        
        return False

    # First fix the __detect_multiple_solutions() method in the Simplex class
    def __detect_multiple_solutions(self) -> bool:
        """
        Check if the problem has multiple optimal solutions.
        This happens when there is a non-basic variable with zero reduced cost (zero in the objective row).
        """
        if not self.__is_solved():
            return False
        
        # First identify which columns correspond to basic variables
        basic_columns = set()
        for i in range(len(self.__tableau) - 1):  # For each constraint row
            # Find the basic variable in this row (if any)
            for j in range(len(self.__tableau[0]) - 1):  # For each column except RHS
                if abs(self.__tableau[i][j] - 1.0) < 1e-10:  # Close to 1 (accounting for floating point)
                    # Check if this is a basic variable column (unit column)
                    is_unit = True
                    for k in range(len(self.__tableau) - 1):
                        if k != i and abs(self.__tableau[k][j]) > 1e-10:  # Not close to 0
                            is_unit = False
                            break
                    if is_unit:
                        basic_columns.add(j)
                        break
        
        # Now check if any non-basic variable has a zero reduced cost
        for j in range(len(self.__tableau[0]) - 1):  # For each column except RHS
            if j not in basic_columns and abs(self.__tableau[-1][j]) < 1e-10:
                # Non-basic with zero cost
                return True
        
        return False
    def __detect_degeneracy(self) -> bool:
        """Check if the solution is degenerate by looking for basic variables with value 0."""
        # First identify basic variables
        basic_vars = []
        for j in range(len(self.__tableau[0]) - 1):
            for i in range(len(self.__tableau) - 1):
                if self.__tableau[i][j] == 1:
                    # Check if this is a unit column
                    is_unit_column = True
                    for k in range(len(self.__tableau) - 1):
                        if k != i and self.__tableau[k][j] != 0:
                            is_unit_column = False
                            break
                    if is_unit_column:
                        basic_vars.append((i, j))
                        break
        
        # Check if any basic variable has value 0
        for i, j in basic_vars:
            if self.__tableau[i][-1] == 0:
                return True
        
        return False
    def __detect_cycling(self, history) -> bool:
        def tableau_signature(tableau):
            # Round all entries to avoid floating point issues and flatten the tableau
            return tuple(tuple(round(float(cell), 6) for cell in row) for row in tableau)

        signature = tableau_signature(self.__tableau)
        if signature in history:
            print("Cycling detected!")  # Optional debug
            return True
        history.add(signature)
        return False

