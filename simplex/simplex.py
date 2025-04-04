from typing import Optional

from simplex import SimplexObjectiveFunction, SimplexConstraintFunction, SimplexSolution, SimplexNotFeasible, \
    SimplexSolutions, SimplexVariableDomains, SimplexOperators


class Simplex:
    def __init__(self):
        self.__tableau: Optional[list[list[float]]] = None
        self.__pivot = None
        self.num_vars: int = -1
        self.objective_function: Optional[SimplexObjectiveFunction] = None
        self.constraints: Optional[list[SimplexConstraintFunction]] = None
        self.domains = None
        self.number_of_slack_variables: int = 0

    def solve(self) -> SimplexSolution:
        self.__tableau = self.__create_tableau()

        if self.__check_if_two_step():
            self.__tableau = self.__solve_first_phase()

        while not self.__is_solved():
            pivot = self.__find_pivot()
            if pivot[1] < 0:
                return SimplexNotFeasible()

            self.__fix_pivot(pivot)

        return self.__get_solution()

    def __is_solved(self):
        is_solved = True

        for i, x in enumerate(self.__tableau[-1]):
            if x < 0 and i != len(self.__tableau[-1]) - 1:
                is_solved = False

        return is_solved

    def __find_pivot(self) -> tuple[int, int]:
        entering_indx = self.__get_entering_var()
        leaving_indx = self.__get_leaving_var(entering_indx)
        return entering_indx, leaving_indx

    def __fix_pivot(self, pivot_indx: tuple[int, int]):
        j, i = pivot_indx

        pivot = self.__tableau[i][j]
        self.__tableau[i] = [element / pivot for element in self.__tableau[i]]

        for indx, row in enumerate(self.__tableau):
            if indx != i:
                row_scale = [y * self.__tableau[indx][j] for y in self.__tableau[i]]
                self.__tableau[indx] = [x - y for x, y in zip(self.__tableau[indx], row_scale)]

    def __get_solution(self) -> SimplexSolutions:
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
                            solution[f"x{j + 1}"] = row[-1]

        print(solution)

        return SimplexSolutions(self.__tableau[-1][-1])

    def __str__(self):
        str_rep = f"""
{self.objective_function}
/
"""
        for constraint in self.constraints:
            str_rep += f"{constraint}\n"

        str_rep += "--------\n"

        for indx, domain in enumerate(self.domains):
            match domain:
                case SimplexVariableDomains.GREATER_THAN_ZERO:
                    str_rep += f"x{indx + 1} >= 0\n"
                case SimplexVariableDomains.LESS_THAN_ZERO:
                    str_rep += f"x{indx + 1} <= 0\n"
                case SimplexVariableDomains.UNRESTRICTED:
                    str_rep += f"x{indx + 1} in R\n"

        return str_rep

    def __create_tableau(self) -> list[list[float]]:
        tableau = []
        slack_to_add: list[tuple[int, int]] = []
        artificial_to_add: list[int] = []
        for indx, constraint in enumerate(self.constraints):
            if constraint.operator == SimplexOperators.LESS_THAN_OR_EQUAL:
                slack_to_add.append((1, indx))
            elif constraint.operator == SimplexOperators.GREATER_THAN_OR_EQUAL:
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
            i_arr = [0] * (self.num_vars - len(artificial_to_add)) + ([-1] * len(artificial_to_add)) + [0]
            for indx in artificial_to_add:
                # print(tableau[indx])
                i_arr = [-(i_arr[i] + val) for i, val in enumerate(tableau[indx])]
            tableau.append(i_arr)

        return tableau

    def __get_entering_var(self):
        z_arr = self.__tableau[-1]
        smallest_indx = 0
        smallest = z_arr[smallest_indx]

        for indx, val in enumerate(z_arr[:-1]):
            if val < smallest:
                smallest = val
                smallest_indx = indx

        return smallest_indx

    def __get_leaving_var(self, entering_indx) -> int:
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
        for i, constraint in enumerate(self.constraints):
            constraint.values.insert(len(constraint.values) - 1, sign if i == indx else 0)

        self.objective_function.values.insert(len(self.objective_function.values) - 1, 0)
        self.num_vars += 1

    def __add_artificial_variable(self, indx: int):
        for i, constraint in enumerate(self.constraints):
            constraint.values.insert(len(constraint.values) - 1, 1 if i == indx else 0)

        self.objective_function.values.insert(len(self.objective_function.values) - 1, 0)
        self.num_vars += 1

    def __check_if_two_step(self) -> bool:
        for constraint in self.constraints:
            if (constraint.operator == SimplexOperators.EQUAL
                    or constraint.operator == SimplexOperators.GREATER_THAN_OR_EQUAL):
                return True
        return False

    def __solve_first_phase(self) -> list[list[float]]:
        number_of_artificial_variables = 0
        for constraint in self.constraints:
            if constraint.operator == SimplexOperators.EQUAL or constraint.operator == SimplexOperators.GREATER_THAN_OR_EQUAL:
                number_of_artificial_variables += 1

        if number_of_artificial_variables == 0:
            return self.__tableau

        while not self.__is_solved():
            pivot = self.__find_first_phase_pivot()
            if pivot[1] < 0:
                # TODO pivot less than 0 error fix
                raise ValueError("Error pivot less than 0")

            self.__fix_pivot(pivot)

        if self.__tableau[-1][-1] != 0:
            # TODO first phase failed error
            raise ValueError("first phase failed error")

        self.__tableau = self.__tableau[:-1]

        for row in self.__tableau:
            for i in range(number_of_artificial_variables):
                row.pop(-2)

        return self.__tableau

    def __find_first_phase_pivot(self):
        entering_indx = self.__get_entering_var()
        leaving_indx = self.__get_leaving_var_first_phase(entering_indx)
        return entering_indx, leaving_indx

    def __get_leaving_var_first_phase(self, entering_indx):
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
