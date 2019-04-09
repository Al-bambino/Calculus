from Lexer import Lexer
from Library import Library
from TokenTypes import TokenType


class Interpreter:
    COMPARISON_OPERATORS = (TokenType.LESS, TokenType.GREATHER, TokenType.EQUAL,
                            TokenType.NOT_EQUAL, TokenType.LESS_EQ, TokenType.GREATHER_EQ)

    def __init__(self, lexer, state, memory):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.state = state
        self.memory = memory
        self.activeVars = []
        self.lib = Library()

    def error(self):
        raise Exception('Greska u parsiranju')

    def eat(self, type):
        if self.current_token.type == type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def is_callable(self, word):
        return True if word in Library.RESERVED_METHOD_WORDS and self.current_token.type == TokenType.LPAREN else False

    def resolve_function(self, word):
        self.eat(TokenType.LPAREN)
        first_argument = self.current_token.value
        self.eat(TokenType.STRING)
        res = getattr(self.lib, word)(first_argument)
        self.eat(TokenType.RPAREN)
        return res

    def factor(self):
        token = self.current_token

        if token.type == TokenType.STRING:
            word = token.value
            self.eat(TokenType.STRING)
            # print(self.current_token.value)
            if self.is_callable(word):
                return self.resolve_function(word)
            # it's var
            if self.current_token.type == TokenType.ASSIGN:
                self.eat(TokenType.ASSIGN)
                result = self.expr()
                self.memory[word] = result
                return result
            return self.memory[word]

        elif token.type == TokenType.INTEGER:
            self.eat(TokenType.INTEGER)
            # print("FACTOR: " + str(token.value))
            return token.value
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            result = self.bool()
            self.eat(TokenType.RPAREN)
            return result

    def term(self):
        result = self.factor()
        # print("TERM got result: " + str(result))
        # print("TERM curr token: " + str(self.current_token.value))

        while self.current_token.type in (TokenType.MUL, TokenType.DIV):
            token = self.current_token
            # print("TERM: " + str(token.value))
            if token.type == TokenType.MUL:
                self.eat(TokenType.MUL)
                result = result * self.factor()
            elif token.type == TokenType.DIV:
                self.eat(TokenType.DIV)
                result = result // self.factor()
            else:
                self.error()

        return result

    def expr(self):

        result = self.term()
        # print("EXPR got result: " + str(result))
        # print("EXPR curr token: " + str(self.current_token.value))
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            # print("EXPR: " + str(token.value))

            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
                result = result + self.term()
            elif token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)
                result = result - self.term()
            else:
                self.error()

        return result

    def bool(self):
        result = True
        left = self.expr()

        if self.current_token.type in Interpreter.COMPARISON_OPERATORS:
            right = None
            while self.current_token.type in Interpreter.COMPARISON_OPERATORS:
                if self.current_token.type == TokenType.LESS:
                    self.eat(TokenType.LESS)
                    right = self.expr()
                    if not (left < right):
                        result = False
                    left = right
                elif self.current_token.type == TokenType.GREATHER:
                    self.eat(TokenType.GREATHER)
                    right = self.expr()
                    if not (left > right):
                        result = False
                    left = right
                elif self.current_token.type == TokenType.EQUAL:
                    self.eat(TokenType.EQUAL)
                    right = self.expr()
                    if not (left == right):
                        result = False
                    left = right
                elif self.current_token.type == TokenType.NOT_EQUAL:
                    self.eat(TokenType.NOT_EQUAL)
                    right = self.expr()
                    if not (left != right):
                        result = False
                    left = right
                elif self.current_token.type == TokenType.LESS_EQ:
                    self.eat(TokenType.LESS_EQ)
                    right = self.expr()
                    if not (left <= right):
                        result = False
                    left = right
                elif self.current_token.type == TokenType.GREATHER_EQ:
                    self.eat(TokenType.GREATHER_EQ)
                    right = self.expr()
                    if not (left >= right):
                        result = False
                    left = right

            return result
        else:
            return left

    def evaluate(self):
        if self.state == "POSTFIX":
            self.postfix_to_infix(self.lexer.text)
        elif self.state == "PREFIX":
            self.prefix_to_infix(self.lexer.text)
        return self.bool()

    def postfix_to_infix(self, exp):
        output = []
        self.lexer = Lexer(exp)
        self.current_token = self.lexer.get_next_token()
        while True:
            if self.current_token.type == TokenType.EOF:
                break
            if self.current_token.type == TokenType.STRING:
                word = self.current_token.value
                self.eat(TokenType.STRING)
                if word in Library.RESERVED_METHOD_WORDS:
                    try:
                        self.eat(TokenType.LPAREN)
                        word += "(" + self.current_token.value + ")"
                        self.eat(TokenType.STRING)
                        self.eat(TokenType.RPAREN)
                    except Exception:
                        pass
                output.append(word)
                # print(output)

            elif self.current_token.type == TokenType.INTEGER:
                output.append(self.current_token.value)
                self.eat(TokenType.INTEGER)
            else:
                operand1 = str(output.pop())
                try:
                    operand2 = str(output.pop())
                    operator = str(self.current_token.value)
                    self.current_token = self.lexer.get_next_token()
                    expression = '(' + operand2 + operator + operand1 + ')'
                    output.append(expression)
                except IndexError:
                    if operand1.isalnum():
                        output.append(operand1)
            # print(output)
        self.lexer = Lexer(output[0])
        self.current_token = self.lexer.get_next_token()
        # print(self.lexer.text)

    def rev_input(self, text):
        self.lexer = Lexer(text)
        self.current_token = self.lexer.get_next_token()
        rev_text = ''
        while self.current_token.type is not TokenType.EOF:
            word = self.current_token.value
            # print("Word je " + str(word))
            if self.current_token.type is TokenType.STRING:
                # print('String je')
                self.eat(TokenType.STRING)
                # print("Curr token je " + str(self.current_token.value))
                if word in Library.RESERVED_METHOD_WORDS:
                    # print("Rez rec")
                    try:
                        self.eat(TokenType.LPAREN)
                        word += "(" + self.current_token.value + ")"
                        self.eat(TokenType.STRING)
                        self.eat(TokenType.RPAREN)

                    except Exception:
                        pass
                # print("Appendujem " + str(word))
                rev_text = ' ' + str(word) + rev_text
            else:
                # print("Appendujem " + str(word))
                rev_text = ' ' + str(word) + rev_text
                self.current_token = self.lexer.get_next_token()
        # print(rev_text)
        return rev_text

    def prefix_to_infix(self, pre_exp):
        stack = []
        rev_input = self.rev_input(pre_exp)
        # print("Reversed: " + rev_input)
        self.lexer = Lexer(rev_input)
        self.current_token = self.lexer.get_next_token()

        while True:
            if self.current_token.type is TokenType.EOF:
                break
            if self.current_token.type is TokenType.STRING:
                word = self.current_token.value
                self.eat(TokenType.STRING)
                if word in Library.RESERVED_METHOD_WORDS:
                    try:
                        self.eat(TokenType.LPAREN)
                        word += "(" + self.current_token.value + ")"
                        self.eat(TokenType.STRING)
                        self.eat(TokenType.RPAREN)
                    except Exception:
                        pass
                stack.append(word)
                # print(output)
            elif self.current_token.type is TokenType.INTEGER:
                stack.append(self.current_token.value)
                self.eat(TokenType.INTEGER)
            else:
                op1 = stack.pop()
                op2 = stack.pop()
                temp = "(" + str(op1) + str(self.current_token.value) + str(op2) + ")"
                self.current_token = self.lexer.get_next_token()
                stack.append(temp)

        k = stack.pop()
        # print(k)
        self.lexer = Lexer(k)
        self.current_token = self.lexer.get_next_token()
