from typing import Optional, Self

from simplex import SimplexObjectiveFunction, SimplexConstraintFunction, SimplexVariableDomains, SimplexMaxOrMin
from simplex.simplex import Simplex


class SimplexBuilder:
    def __init__(self):
        self.__objective_function: Optional[SimplexObjectiveFunction] = None
        self.__constraints: list[SimplexConstraintFunction] = []
        self.__num_vars: int = -1
        self.__domains: list[SimplexVariableDomains] = []

    def set_number_of_vars(self, num_var: int, *domains: SimplexVariableDomains) -> Self:
        if self.__num_vars > 0:
            raise ValueError("The number of variables has already been set")

        if num_var <= 0:
            raise ValueError("Please enter a valid value for the number of variables (>0)")

        if num_var != len(domains):
            raise ValueError("Number of inputted variable domains should match the number of variable")

        self.__num_vars = num_var
        self.__domains = list(domains)

        return self

    def set_objective_function(self, objective_function: SimplexObjectiveFunction) -> Self:
        if self.__num_vars <= 0:
            raise ValueError("Please enter a valid value for the number of variables (>0)")

        if objective_function.num_vars != self.__num_vars:
            raise ValueError("Constraint doesn't contain the same amount of variables specified")

        self.__objective_function = objective_function
        return self

    def add_constraint(self, constraint: SimplexConstraintFunction) -> Self:
        if self.__num_vars <= 0:
            raise ValueError("Please enter a valid value for the number of variables (>0)")

        if constraint.num_vars != self.__num_vars:
            raise ValueError("Constraint doesn't contain the same amount of variables specified")

        self.__constraints.append(constraint)
        return self

    def set_to_standard_form(self, verbose: bool = False) -> Self:
        if verbose:
            # TODO Write error messages
            raise NotImplementedError()

        if self.__domains is None:
            # TODO Write error message
            raise ValueError()

        new_domains: list[SimplexVariableDomains] = []
        for indx, domain in enumerate(self.__domains):
            match domain:
                case SimplexVariableDomains.GREATER_THAN_ZERO:
                    new_domains.append(domain)
                    continue
                case SimplexVariableDomains.LESS_THAN_ZERO:
                    self.__fix_domain_less_than_zero(indx)
                    new_domains.append(SimplexVariableDomains(SimplexVariableDomains.GREATER_THAN_ZERO))
                    continue
                case SimplexVariableDomains.UNRESTRICTED:
                    self.__fix_domain_unrestricted(indx)
                    new_domains.append(SimplexVariableDomains(SimplexVariableDomains.GREATER_THAN_ZERO))
                    new_domains.append(SimplexVariableDomains(SimplexVariableDomains.GREATER_THAN_ZERO))
                    continue

        self.__domains = new_domains
        self.__num_vars = len(new_domains)

        if self.__objective_function.operator == SimplexMaxOrMin.MIN:
            self.__fix_min_to_max()

        return self

    def build(self) -> Simplex:
        if self.__num_vars <= 0:
            raise ValueError("No variables provided")

        if self.__domains is None:
            raise ValueError("No domains for the variables were inputted")

        if self.__objective_function is None:
            raise ValueError("Objective function for simplex not provided")

        if len(self.__constraints) == 0:
            raise ValueError("No constraints provided")

        simplex = Simplex()
        simplex.num_vars = self.__num_vars
        simplex.objective_function = self.__objective_function
        simplex.constraints = self.__constraints
        simplex.domains = self.__domains

        return simplex

    def __fix_domain_less_than_zero(self, indx: int) -> None:
        # TODO Check if correct
        assert indx <= len(self.__objective_function.values)

        self.__objective_function.values[indx] *= -1

        for constraint in self.__constraints:
            assert indx <= len(constraint.values)
            constraint.values[indx] *= -1

    def __fix_domain_unrestricted(self, indx: int) -> None:
        # TODO Check if correct
        assert indx <= len(self.__objective_function.values)

        values = self.__objective_function.values
        values.insert(indx, -values[indx])

        new_constraints = []
        for constraint in self.__constraints:
            assert indx <= len(constraint.values)
            constraint_values = constraint.values
            constraint_values.insert(indx, -constraint_values[indx])
            new_constraints.append(SimplexConstraintFunction(constraint.operator, *constraint_values))

        self.__constraints = new_constraints

    def __fix_min_to_max(self):
        values = self.__objective_function.values
        values = map(lambda x: -x, values)
        self.__objective_function = SimplexObjectiveFunction(SimplexMaxOrMin(SimplexMaxOrMin.MAX), *values)
