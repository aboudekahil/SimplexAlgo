from enum import Enum, auto
from typing import Optional

from simplex import Simplex, MaxOrMin, SimplexBuilder, VariableDomains, ObjectiveFunction, ConstraintFunction, Operators


class LPParsingError(Exception):
    pass


class TokenType(Enum):
    DECIMAL = auto()
    MAX = auto()
    MIN = auto()
    PLUS = auto()
    MINUS = auto()
    EQUAL = auto()
    LEQ = auto()
    GEQ = auto()
    IDENTIFIER = auto()
    NUMBER = auto()
    NEW_LINE = auto()
    EOF = auto()
    UNRESTRICTED = auto()

    def is_num(self):
        return self == self.NUMBER or self == self.DECIMAL

    def is_sign(self):
        return self == self.MINUS or self == self.PLUS

    def is_operator(self):
        return self == self.EQUAL or self == self.GEQ or self == self.LEQ


class Token:
    def __init__(self, token_type: TokenType, lexem: str):
        self.token_type = token_type
        self.lexem = lexem

    def __str__(self):
        return f"{self.token_type}: {self.lexem}"

    def __repr__(self):
        return f"{self.token_type}: {self.lexem.__repr__()}"


class Variable:
    def __init__(self, indx: int, domain: Optional[VariableDomains]):
        self.indx = indx
        self.domain = domain


class Term:
    def __init__(self, coefficient: float, variable: Optional[Variable] = None):
        self.coefficient = coefficient
        self.variable = variable


class Formula:
    def __init__(self):
        self.terms: list[Term] = []

    def add_term(self, term: Term):
        self.terms.append(term)


class Constraint:
    def __init__(self, left: Formula, operator: TokenType, right: Formula):
        self.left: Formula = left
        self.operator: Operators = Operators.EQUAL

        if operator == TokenType.LEQ:
            self.operator = Operators.LEQ
        else:
            self.operator = Operators.GEQ

        self.right = right


class LinearProgram:
    def __init__(self):
        self.variables: dict[int, Variable] = {}
        self.objective_function: Optional[tuple[MaxOrMin, Formula]] = None
        self.constraints: list[Constraint] = []

    def add_variable(self, var: Variable):
        self.variables[var.indx] = var

    def set_objective(self, max_or_min: MaxOrMin, formula: Formula):
        self.objective_function = (max_or_min, formula)

    def add_constraint(self, constraint: Constraint):
        self.constraints.append(constraint)


class LPScanner:
    def __init__(self, text: str):
        self.text = text
        self.current = 0
        self.start = 0
        self.tokens: list[Token] = []
        self.line_number = 0
        self.line_char = 0

    def scan_tokens(self) -> list[Token]:
        while not self.__is_at_end():
            self.start = self.current
            self.__scan_token()

        self.tokens.append(Token(TokenType.EOF, ""))

        return self.tokens

    def __is_at_end(self):
        return self.current >= len(self.text)

    def __scan_token(self):
        c = self.__advance()

        if not c.isascii():
            raise ValueError(f"Non ascii character: {c} at {self.line_number}:{self.line_char}")

        if c == '+':
            self.__add_token(TokenType.PLUS)
        elif c == '=':
            self.__add_token(TokenType.EQUAL)
        elif c == '-':
            self.__add_token(TokenType.MINUS)
        elif c == '\n':
            self.line_number += 1
            self.line_char = 0
            self.__add_token(TokenType.NEW_LINE)
        elif c == '>':
            c2 = self.__advance()
            if c2 != '=':
                raise ValueError(
                    f"Token {self.text[self.start:self.current]} unrecognized at {self.line_number}:{self.line_char}, did you mean '>='?")
            self.__add_token(TokenType.GEQ)
        elif c == '<':
            c2 = self.__advance()
            if c2 != '=':
                raise ValueError(
                    f"Token {self.text[self.start:self.current]} unrecognized at {self.line_number}:{self.line_char}, did you mean '<='?")

            self.__add_token(TokenType.LEQ)
        elif c.isdigit():
            while self.__peek().isdigit():
                self.__advance()

            if self.__peek() == '.' and self.__peek_next().isdigit():
                self.__advance()

                while self.__peek().isdigit():
                    self.__advance()

                self.__add_token(TokenType.DECIMAL)
                return

            self.__add_token(TokenType.NUMBER)
        elif c.isalpha():
            self.__identifier()
        elif c.isspace():
            return
        else:
            raise ValueError(f"Unrecognized character: {c} at {self.line_number}:{self.line_char}")

    def __advance(self) -> str:
        self.current += 1
        self.line_char += 1
        return self.text[self.current - 1]

    def __add_token(self, token_type: TokenType):
        text = self.text[self.start: self.current]
        self.tokens.append(Token(token_type, text))

    def __peek(self) -> str:
        if self.__is_at_end(): return '\0'
        return self.text[self.current]

    def __peek_next(self) -> str:
        if self.current + 1 >= len(self.text): return '\0'

        return self.text[self.current + 1]

    def __identifier(self):
        while self.__peek().isalnum():
            self.__advance()

        text = self.text[self.start:self.current]

        if text.lower() == 'min':
            token_type = TokenType.MIN
        elif text.lower() == 'max':
            token_type = TokenType.MAX
        elif text.lower() == "unrestricted":
            token_type = TokenType.UNRESTRICTED
        else:
            token_type = TokenType.IDENTIFIER

        self.__add_token(token_type)

class LPParser:
    def __init__(self, tokens: list[Token]):
        self.__tokens = tokens
        self.__current = 0
        self.__lp = LinearProgram()


    def parse(self) -> Simplex:
        self.__simplex()
        simplex_builder = SimplexBuilder()
        simplex_builder.set_number_of_vars(len(self.__lp.variables),
                                           *[var.domain for var in self.__lp.variables.values()])
        simplex_builder.set_objective_function(ObjectiveFunction(self.__lp.objective_function[0], *self.__term_to_list(
            self.__lp.objective_function[1].terms, len(self.__lp.variables))))

        for constraint in self.__lp.constraints:
            simplex_builder.add_constraint(ConstraintFunction(constraint.operator, *self.__constraint_to_list(constraint,
                                                                                                              len(self.__lp.variables))))

        simplex_builder.set_to_standard_form()
        return simplex_builder.build()

    def __term_to_list(self, term: list[Term], num_var: int) -> list[float]:
        coefs: list[int] = [0] * (num_var + 1)

        for iterm in term:
            if iterm.variable is not None:
                coefs[iterm.variable.indx] = iterm.coefficient
            else:
                coefs[-1] = iterm.coefficient

        return coefs

    def __constraint_to_list(self, constraint: Constraint, num_var: int) -> list[float]:
        coefs = [0] * (num_var + 1)
        left_coef = self.__term_to_list(constraint.left.terms, num_var)

        for indx, n in enumerate(left_coef):
            coefs[indx] = n * (1 if indx < num_var else -1)

        right_coef = self.__term_to_list(constraint.right.terms, num_var)
        for indx, n in enumerate(right_coef):
            coefs[indx] += n * (-1 if indx < num_var else 1)

        return coefs

    def __simplex(self):
        while self.__check(TokenType.NEW_LINE) and not self.__is_at_end():
            self.__advance()

        while self.__check_identifier() and self.__peek().lexem.startswith("x"):
            self.__domain()

            while self.__check(TokenType.NEW_LINE) and not self.__is_at_end():
                self.__advance()

        self.__objective_function()

        while self.__check(TokenType.NEW_LINE) and not self.__is_at_end():
            self.__advance()

        while not self.__is_at_end() and not self.__check(TokenType.EOF):
            self.__constraint()

            while self.__check(TokenType.NEW_LINE) and not self.__is_at_end():
                self.__advance()

    def __domain(self):
        var = self.__variable()

        if self.__check(TokenType.UNRESTRICTED):
            var.domain = VariableDomains.UNRESTRICTED
        elif self.__check(TokenType.LEQ):
            var.domain = VariableDomains.LEQ_THAN_ZERO
        elif self.__check(TokenType.GEQ):
            var.domain = VariableDomains.GEQ_THAN_ZERO
        else:
            raise LPParsingError(
                f"Unrecognized domain for x{var.indx}, only available options are UNRESTRICTED, LEQ, GEQ")

        self.__advance()
        self.__advance()
        self.__lp.add_variable(var)

    def __check(self, token_type: TokenType) -> bool:
        if self.__is_at_end():
            return False

        return self.__peek().token_type == token_type

    def __peek(self) -> Token:
        return self.__tokens[self.__current]

    def __is_at_end(self) -> bool:
        return self.__peek().token_type == TokenType.EOF

    def __advance(self) -> Token:
        if not self.__is_at_end():
            self.__current += 1
        return self.__previous()

    def __previous(self) -> Token:
        return self.__tokens[self.__current - 1]

    def __check_identifier(self):
        if self.__is_at_end():
            return False

        return self.__peek().token_type == TokenType.IDENTIFIER

    def __objective_function(self):
        if not self.__match(TokenType.MAX) and not self.__match(TokenType.MIN):
            raise LPParsingError(f"Expected 'max' or 'min' for objective function, got {self.__peek()}")

        max_min = MaxOrMin.MAX if self.__previous().token_type == TokenType.MAX else MaxOrMin.MIN

        formula = self.__formula()

        self.__lp.set_objective(max_min, formula)

    def __match(self, token_type: TokenType) -> bool:
        if self.__check(token_type):
            self.__advance()
            return True
        return False

    def __variable(self):
        if not self.__check_identifier() or not self.__peek().lexem.startswith('x'):
            raise LPParsingError(f"Expected variable (formal: x<number>), got {self.__peek()}")

        var_token = self.__advance()
        var_name = var_token.lexem

        try:
            index = int(var_name[1:])

            if index in self.__lp.variables:
                return self.__lp.variables[index]
            else:
                return Variable(index, None)
        except ValueError:
            raise LPParsingError(f"Invalid variable name: {var_name}. Expected format: x<number>")

    def __formula(self):
        formula = Formula()

        if self.__match(TokenType.PLUS) or self.__match(TokenType.MINUS):
            sign = 1 if self.__previous().token_type == TokenType.PLUS else -1
            term = self.__unit()
            term.coefficient *= sign
            formula.add_term(term)
        else:
            formula.add_term(self.__unit())

        while self.__match(TokenType.PLUS) or self.__match(TokenType.MINUS):
            sign = 1 if self.__previous().token_type == TokenType.PLUS else -1
            term = self.__unit()
            term.coefficient *= sign
            formula.add_term(term)

        return formula

    def __unit(self) -> Term:
        if self.__check_number():
            number = self.__parse_number()

            if self.__check_identifier() and self.__peek().lexem.startswith('x'):
                var = self.__variable()
                if var.indx >= len(self.__lp.variables):
                    raise LPParsingError(f"Variable x{var.indx} does not exist")
                return Term(number, var)
            else:
                return Term(number)

        elif self.__check_identifier() and self.__peek().lexem.startswith('x'):
            var = self.__variable()
            if var.indx >= len(self.__lp.variables):
                raise LPParsingError(f"Variable x{var.indx} does not exist")
            return Term(1.0, var)
        else:
            raise LPParsingError(f"Expected a number or variable, got {self.__peek()} ")

    def __constraint(self):
        left = self.__formula()

        if not self.__match_operator():
            raise LPParsingError(f"Expected operator (=, <=, >=) in constraint, got {self.__peek()}")

        operator = self.__previous().token_type

        right = self.__formula()

        constraint = Constraint(left, operator, right)

        self.__lp.add_constraint(constraint)

    def __match_operator(self):
        if self.__check(TokenType.EQUAL) or self.__check(TokenType.LEQ) or self.__check(TokenType.GEQ):
            self.__advance()
            return True
        return False

    def __check_number(self):
        if self.__is_at_end():
            return False
        return self.__peek().token_type == TokenType.NUMBER or self.__peek().token_type == TokenType.DECIMAL

    def __parse_number(self):
        if self.__match(TokenType.NUMBER) or self.__match(TokenType.DECIMAL):
            return float(self.__previous().lexem)
        else:
            raise LPParsingError(f"Expected a number, got {self.__peek()}")


if __name__ == "__main__":
    a = LPParser(LPScanner("""
        x0 >= 0
        x1 >= 0
        max 3x0+2x1+
        
        
        
        
        x0+x1<=100
        """).scan_tokens()).parse()

    print(a.solve().values)
