from Interpreter import Interpreter
from collections import defaultdict
from Lexer import Lexer


def main():
    memory = defaultdict(int)
    states = ['PREFIX', 'INFIX', 'POSTFIX']
    state = states[1]
    while True:
        try:
            text = input(state + ' --> ')
        except EOFError:
            break

        if not text:
            continue

        command = text.strip().upper()

        if command == 'EXIT':
            break

        if command in states:
            state = command
            continue

        lexer = Lexer(text)
        interpreter = Interpreter(lexer, state, memory)
        result = interpreter.evaluate()
        print(result)


if __name__ == "__main__":
    main()
