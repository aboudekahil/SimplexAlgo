from enum import Enum, auto

from simplex import MaxOrMin, ObjectiveFunction


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
        else:
            token_type = TokenType.IDENTIFIER

        self.__add_token(token_type)


class LPParser:
    def __init__(self, tokens: list[Token]):
        self.__tokens = tokens
        self.current = 0
        self.num_var = -1
        self.constraints = []
        self.domains = None

    def parse(self):
        self.__num_var()
        self.__consume_new_lines()
        self.__objective_function()
        self.__consume_new_lines()
        self.__constraints()

    def __objective_function(self):
        if self.__peek().token_type == TokenType.MAX:
            max_or_min = MaxOrMin.MAX
        elif self.__peek().token_type == TokenType.MIN:
            max_or_min = MaxOrMin.MIN
        else:
            raise ValueError("Objective function doesn't have a max/min operator")

        coefficients = self.__formula()

        self.objective_function = ObjectiveFunction(max_or_min, *coefficients)
        self.__consume(TokenType.NEW_LINE, "Expected a new line after the number of variables")


    def __num_var(self):

        self.num_var = int(self.__consume(TokenType.NUMBER, "Number of variables not set in the beginning.").lexem)

        if self.num_var <= 0:
            raise ValueError("Invalid number of variables set, should be >0")

        self.__consume(TokenType.NEW_LINE, "Expected a new line after the number of variables")

    def __is_at_end(self) -> bool:
        return self.__peek().token_type == TokenType.EOF

    def __peek(self) -> Token:
        return self.__tokens[self.current]

    def __peek_next(self) -> Token:
        if self.__is_at_end():
            return self.__tokens[-1]
        return self.__tokens[self.current + 1]

    def __consume(self, token_type: TokenType, error_message: str) -> Token:
        if self.__check(token_type):
            return self.__advance()

        raise ValueError(error_message)

    def __advance(self) -> Token:
        if not self.__is_at_end():
            self.current += 1
        else:
            return self.__tokens[-1]

        return self.__tokens[self.current - 1]

    def __check(self, token_type: TokenType) -> bool:
        if self.__is_at_end():
            return False
        return self.__peek().token_type == token_type

    def __consume_new_lines(self):
        while self.__check(TokenType.NEW_LINE):
            self.__advance()

    def __formula(self) -> list[float]:
        coefficients = [0] * (self.num_var + 1)
        token = self.__advance()
        if token.token_type == TokenType.IDENTIFIER:
            var_name = token.lexem
            var_index = int(var_name[1:])
            if var_index <= 0 or var_index > self.num_var:
                raise ValueError("Invalid variable name syntax")

            coefficients[var_index] += 1
        elif token.token_type == TokenType.MINUS:
            next_token = self.__advance()
            if next_token.token_type == TokenType.IDENTIFIER:
                var_name = token.lexem
                var_index = int(var_name[1:])
                if var_index <= 0 or var_index > self.num_var:
                    raise ValueError("Invalid variable name")

                coefficients[var_index] += -1

            elif next_token.token_type.is_num():
                coef = float(next_token.lexem)

                if self.__peek().token_type != TokenType.IDENTIFIER:
                    raise ValueError("Invalid formula syntax")

                ident_token = self.__advance()

                var_name = ident_token.lexem
                var_index = int(var_name[1:])
                if var_index <= 0 or var_index > self.num_var:
                    raise ValueError("Invalid variable name syntax")

                coefficients[var_index] += -coef

            else:
                raise ValueError("Invalud formula syntax")
        elif token.token_type == TokenType.PLUS:
            next_token = self.__advance()
            if next_token.token_type == TokenType.IDENTIFIER:
                var_name = token.lexem
                var_index = int(var_name[1:])
                if var_index <= 0 or var_index > self.num_var:
                    raise ValueError("Invalid variable name")

                coefficients[var_index] += 1

            elif next_token.token_type.is_num():
                coef = float(next_token.lexem)

                if self.__peek().token_type != TokenType.IDENTIFIER:
                    raise ValueError("Invalid formula syntax")

                ident_token = self.__advance()

                var_name = ident_token.lexem
                var_index = int(var_name[1:])
                if var_index <= 0 or var_index > self.num_var:
                    raise ValueError("Invalid variable name syntax")

                coefficients[var_index] += coef

            else:
                raise ValueError("Invalud formula syntax")
        elif token.token_type.is_num():
            coef = float(token.lexem)

            if self.__peek().token_type.is_sign():
                coefficients[-1] += coef
            elif self.__peek().token_type != TokenType.IDENTIFIER:
                raise ValueError("Invalid formula syntax")

            ident_token = self.__advance()

            var_name = ident_token.lexem
            var_index = int(var_name[1:])
            if var_index <= 0 or var_index > self.num_var:
                raise ValueError("Invalid variable name syntax")

            coefficients[var_index] += coef
        else:
            raise ValueError("Invalid formula syntax")

        while not (self.__peek().token_type == TokenType.NEW_LINE
                   or self.__peek().token_type.is_operator()):
            token = self.__advance()

            if token.token_type == TokenType.MINUS:
                next_token = self.__advance()
                if next_token.token_type == TokenType.IDENTIFIER:
                    var_name = token.lexem
                    var_index = int(var_name[1:])
                    if var_index <= 0 or var_index > self.num_var:
                        raise ValueError("Invalid variable name")

                    coefficients[var_index] += -1

                elif next_token.token_type.is_num():
                    coef = float(next_token.lexem)

                    if self.__peek().token_type != TokenType.IDENTIFIER:
                        raise ValueError("Invalid formula syntax")

                    ident_token = self.__advance()

                    var_name = ident_token.lexem
                    var_index = int(var_name[1:])
                    if var_index <= 0 or var_index > self.num_var:
                        raise ValueError("Invalid variable name syntax")

                    coefficients[var_index] += -coef

                else:
                    raise ValueError("Invalud formula syntax")
            elif token.token_type == TokenType.PLUS:
                next_token = self.__advance()
                if next_token.token_type == TokenType.IDENTIFIER:
                    var_name = token.lexem
                    var_index = int(var_name[1:])
                    if var_index <= 0 or var_index > self.num_var:
                        raise ValueError("Invalid variable name")

                    coefficients[var_index] += 1

                elif next_token.token_type.is_num():
                    coef = float(next_token.lexem)

                    if self.__peek().token_type != TokenType.IDENTIFIER:
                        raise ValueError("Invalid formula syntax")

                    ident_token = self.__advance()

                    var_name = ident_token.lexem
                    var_index = int(var_name[1:])
                    if var_index <= 0 or var_index > self.num_var:
                        raise ValueError("Invalid variable name syntax")

                    coefficients[var_index] += coef

                else:
                    raise ValueError("Invalid formula syntax")

        return coefficients


if __name__ == "__main__":
    print(LPScanner("5\nmax 3x1+2x2\nx1+x2>=0\nx1>=0").scan_tokens())
