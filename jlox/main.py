import argparse
import sys
from jlox.interpreter import Interpreter

from jlox.scanner import Scanner
from jlox.parser import Parser
from jlox.resolver import Resolver
from jlox.errors import JloxRuntimeError, JloxSyntaxError


def get_args():
    parser = argparse.ArgumentParser(
        prog="jlox", description="Interpreter for the jlox language"
    )
    parser.add_argument("script", nargs="?")

    return parser.parse_args()


def run(source: str, interpreter: Interpreter) -> None:
    try:
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()

        parser = Parser(tokens)
        statements = parser.parse()

        if not statements:
            return

        resolver = Resolver(interpreter)
        resolver.resolve(statements)

        interpreter.interpret(statements)
    except JloxRuntimeError as e:
        print(f"Runtime error: {e}")
    except JloxSyntaxError as e:
        print(f"Syntax error: {e}")


def run_file(file: str) -> None:
    interpreter = Interpreter()

    with open(file, "r") as f:
        script = f.read()

    run(script, interpreter)


def run_prompt() -> None:
    interpreter = Interpreter()
    try:
        while (line := input("> ")) != "q":
            run(line, interpreter)
    except (KeyboardInterrupt, EOFError):
        pass


def main():
    args = get_args()

    if args.script:
        run_file(args.script)
    else:
        run_prompt()


if __name__ == "__main__":
    main()
