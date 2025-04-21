from typing import Optional, Self, Union

from simplex import ObjectiveFunction, ConstraintFunction, VariableDomains, MaxOrMin
from simplex.simplex_class import Simplex


class SimplexBuilder:
    def __init__(self):
        """
        Constructs the simplex builder to build the simplex.
        """
        self.__objective_function: Optional[ObjectiveFunction] = None
        self.__constraints: list[ConstraintFunction] = []
        self.__num_vars: int = -1
        self.__domains: list[VariableDomains] = []
        self.__was_min = False

    def set_number_of_vars(self, num_var: int, *domains: VariableDomains) -> Self:
        """
        Sets the number of variables in the problem and their domains.
        :param num_var: the number of variables
        :param domains: the domains of the variables respectively
        :return: The builder itself
        """
        if self.__num_vars > 0:
            raise ValueError("The number of variables has already been set")

        if num_var <= 0:
            raise ValueError("Please enter a valid value for the number of variables (>0)")

        if num_var != len(domains):
            raise ValueError("Number of inputted variable domains should match the number of variable")

        self.__num_vars = num_var
        self.__domains = list(domains)

        return self

    def set_objective_function(self, objective_function: ObjectiveFunction) -> Self:
        """
        Sets the objective function for the problem
        :param objective_function: The objective function
        :return: The simplex builder
        """
        if self.__num_vars <= 0:
            raise ValueError("Please enter a valid value for the number of variables (>0)")

        if objective_function.num_vars != self.__num_vars:
            raise ValueError("Constraint doesn't contain the same amount of variables specified")

        self.__objective_function = objective_function
        return self

    def add_constraint(self, constraint: ConstraintFunction) -> Self:
        """
        Adds a constraint to the problem.
        :param constraint: the constraint to add.
        :return: the simplex builder.
        """
        if self.__num_vars <= 0:
            raise ValueError("Please enter a valid value for the number of variables (>0)")

        if constraint.num_vars != self.__num_vars:
            raise ValueError("Constraint doesn't contain the same amount of variables specified")

        self.__constraints.append(constraint)
        return self

    def set_to_standard_form(self, verbose: bool = False) -> Self:
        """
        Standardizes the problem.
        :param verbose: Outputs the standardization process.
        :return: The simplex builder
        """
        if verbose:
            # TODO Write error messages
            raise NotImplementedError()

        if self.__domains is None:
            # TODO Write error message
            raise ValueError()

        new_domains: list[VariableDomains] = []
        for indx, domain in enumerate(self.__domains):
            match domain:
                case VariableDomains.GEQ_THAN_ZERO:
                    new_domains.append(domain)
                    continue
                case VariableDomains.LEQ_THAN_ZERO:
                    self.__fix_domain_less_than_zero(indx)
                    new_domains.append(VariableDomains(VariableDomains.GEQ_THAN_ZERO))
                    continue
                case VariableDomains.UNRESTRICTED:
                    self.__fix_domain_unrestricted(indx)
                    new_domains.append(VariableDomains(VariableDomains.GEQ_THAN_ZERO))
                    new_domains.append(VariableDomains(VariableDomains.GEQ_THAN_ZERO))
                    continue

        self.__domains = new_domains
        self.__num_vars = len(new_domains)

        if self.__objective_function.operator == MaxOrMin.MIN:
            self.__was_min = True
            self.__fix_min_to_max()

        return self

    @staticmethod
    def parse_text(text: str) -> Simplex:
        """
        Parses text and constructs the object
        :param text: text to parse
        """
        from simplex.LPParser import LPParser, LPScanner

        return LPParser(LPScanner(text).scan_tokens()).parse()

    def build(self) -> Simplex:
        """
        Returns the simplex
        :return: the simplex you built
        """
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
        simplex.was_min = self.__was_min

        return simplex

    def __fix_domain_less_than_zero(self, indx: int) -> None:
        """
        Fixes if the domain of a variable if it's less than 0
        :param indx: the index of the variable to fix.
        """
        # TODO Check if correct
        assert indx <= len(self.__objective_function.values)

        self.__objective_function.values[indx] *= -1

        for constraint in self.__constraints:
            assert indx <= len(constraint.values)
            constraint.values[indx] *= -1

    def __fix_domain_unrestricted(self, indx: int) -> None:
        """
        Fixes the variable if it is unrestricted.
        :param indx: the index of the variable
        """
        # TODO Check if correct
        assert indx <= len(self.__objective_function.values)

        values = self.__objective_function.values
        values.insert(indx, -values[indx])

        new_constraints = []
        for constraint in self.__constraints:
            assert indx <= len(constraint.values)
            constraint_values = constraint.values
            constraint_values.insert(indx, -constraint_values[indx])
            new_constraints.append(ConstraintFunction(constraint.operator, *constraint_values))

        self.__constraints = new_constraints

    def __fix_min_to_max(self):
        """
        Changes min to max in the objective function
        """
        values = self.__objective_function.values
        values = map(lambda x: -x, values)
        self.__objective_function = ObjectiveFunction(MaxOrMin(MaxOrMin.MAX), *values)


    def __add_var(self, domain: VariableDomains):
        self.__num_vars += 1
        self.__domains.append(domain)

