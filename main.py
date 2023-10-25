import math


class OperatorPrecedence:
    def __init__(self):
        self.precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}

    def get_precedence(self, operator):
        return self.precedence.get(operator, 0)


class Tokenizer:
    def __init__(self, operators):
        self.operators = list(operators) + ['sin', 'cos', 'tan', 'log']

    def tokenize_generator(self, expression):
        for operator in self.operators:
            expression = expression.replace(operator, f' {operator} ')
        return (token for token in expression.replace('(', ' ( ').replace(')', ' ) ').split())

    def is_variable(self, token):
        return token.islower() and token not in self.operators

    def is_function(self, token):
        return token.islower() and token in {'sin', 'cos', 'tan', 'log'}


class InfixToPostfixConverter:
    def __init__(self, operator_precedence, tokenizer):
        self.operator_precedence = operator_precedence
        self.tokenizer = tokenizer

    def convert(self, infix_tokens):
        output = []
        operator_stack = []
        get_precedence = self.operator_precedence.get_precedence

        for token in infix_tokens:
            if token.replace('.', '', 1).isdigit() or self.tokenizer.is_variable(token):
                output.append(token)
            elif token in self.operator_precedence.precedence:
                while operator_stack and get_precedence(operator_stack[-1]) >= get_precedence(token):
                    output.append(operator_stack.pop())
                operator_stack.append(token)
            elif self.tokenizer.is_function(token):
                operator_stack.append(token)
            elif token == '(':
                operator_stack.append(token)
            elif token == ')':
                while operator_stack and operator_stack[-1] != '(':
                    output.append(operator_stack.pop())
                if operator_stack and operator_stack[-1] == '(':
                    operator_stack.pop()
                else:
                    raise ValueError("Mismatched parentheses")
            else:
                raise ValueError(f"Unknown token {token}")

        while operator_stack:
            output.append(operator_stack.pop())

        return output


class PostfixEvaluator:
    def __init__(self, default_variables=None):
        self.variables = default_variables or {}

    def evaluate(self, postfix_tokens):
        stack = []

        for token in postfix_tokens:
            if token.replace('.', '', 1).isdigit():
                stack.append(float(token))
            elif token.islower() and token in {'sin', 'cos', 'tan', 'log'}:
                if token == 'sin':
                    operand = stack.pop()
                    stack.append(math.sin(math.radians(operand)))
                elif token == 'cos':
                    operand = stack.pop()
                    stack.append(math.cos(math.radians(operand)))
                elif token == 'tan':
                    operand = stack.pop()
                    stack.append(math.tan(math.radians(operand)))
                elif token == 'log':
                    if len(stack) < 1:
                        raise ValueError(f"Insufficient operands for function {token}")
                    operand = stack.pop()
                    if operand <= 0:
                        raise ValueError(f"Invalid operand {operand} for function {token}")
                    stack.append(math.log(operand))
            elif token.islower():
                value = self.variables.get(token, None)
                if value is None:
                    raise ValueError(f"Undefined variable: {token}")
                stack.append(value)
            elif token in {'+', '-', '*', '/'}:
                if len(stack) < 2:
                    raise ValueError(f"Insufficient operands for operator {token}")
                operand2 = stack.pop()
                operand1 = stack.pop()
                if token == '+':
                    stack.append(operand1 + operand2)
                elif token == '-':
                    stack.append(operand1 - operand2)
                elif token == '*':
                    stack.append(operand1 * operand2)
                elif token == '/':
                    if operand2 == 0:
                        raise ValueError("Division by zero")
                    stack.append(operand1 / operand2)
            elif token == '^':
                if len(stack) < 2:
                    raise ValueError("Insufficient operands for operator ^")
                exponent = stack.pop()
                base = stack.pop()
                stack.append(math.pow(base, exponent))
            else:
                raise ValueError(f"Unknown token {token}")

        if len(stack) == 1:
            return stack[0]
        else:
            raise ValueError("Invalid expression")


class Calculator:
    def __init__(self, default_variables=None):
        self.input = ""
        self.result = 0
        self.operator_precedence = OperatorPrecedence()
        self.tokenizer = Tokenizer(self.operator_precedence.precedence.keys())
        self.converter = InfixToPostfixConverter(self.operator_precedence, self.tokenizer)
        self.evaluator = PostfixEvaluator(default_variables)

    def ask(self):
        try:
            self.input = str(input("SmartCalc > "))
            if "=" in self.input:
                self.handle_variable_definition()
            else:
                self.calc()
        except Exception as e:
            print(f"Error: {str(e)}")

    def handle_variable_definition(self):
        try:
            variable, expression = map(str.strip, self.input.split('='))
            infix_tokens = self.tokenizer.tokenize_generator(expression)
            postfix_tokens = self.converter.convert(infix_tokens)
            value = self.evaluator.evaluate(postfix_tokens)
            self.evaluator.variables[variable] = value
            print(f"Variable {variable} defined with value {value}")
            self.result = value
        except ValueError as ve:
            print(f"Variable definition error: {str(ve)}")

    def calc(self):
        try:
            infix_tokens = self.tokenizer.tokenize_generator(self.input)
            postfix_tokens = self.converter.convert(infix_tokens)
            self.result = self.evaluator.evaluate(postfix_tokens)
            print(self.result)
        except ValueError as ve:
            print(f"Calculation error: {str(ve)}")


if __name__ == '__main__':
    default_vars = {'pi': math.pi, 'e': math.e}
    calculator = Calculator(default_variables=default_vars)
    while True:
        calculator.ask()
