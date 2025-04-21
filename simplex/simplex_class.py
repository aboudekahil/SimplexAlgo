from fractions import Fraction
from typing import Optional

from simplex import ObjectiveFunction, ConstraintFunction, Solution, NotFeasible, VariableDomains, Operators, NotBounded


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

        if self.__check_if_two_step():
            self.__tableau = self.__solve_first_phase()

        while not self.__is_solved():
            pivot = self.__find_pivot()
            if pivot[1] < 0:
                return NotFeasible()

            self.__fix_pivot(pivot)

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

        while not self.__is_solved():
            pivot = self.__find_first_phase_pivot()
            if pivot[1] < 0:
                # TODO pivot less than 0 error fix
                raise NotBounded()

            self.__fix_pivot(pivot)

        if self.__tableau[-1][-1] != 0:
            # TODO first phase failed error
            raise NotFeasible()

        self.__tableau = self.__tableau[:-1]

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
