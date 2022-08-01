import argparse
import sys

from jlox.scanner import Scanner

had_error = [False]


def get_args():
    parser = argparse.ArgumentParser(
        prog="jlox", description="Interpreter for the jlox language"
    )
    parser.add_argument("script", nargs="?")

    return parser.parse_args()


def report(line: int, where: str, message: str) -> None:
    print(f"[line {line}] Error{where}: {message}")
    had_error[0] = True


def error(line: int, message: str) -> None:
    report(line, "", message)


def run(source: str) -> None:
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()

    print(tokens)


def run_file(file: str) -> None:
    with open(file, "r") as f:
        script = f.read()

    run(script)

    if had_error[0]:
        sys.exit(65)


def run_prompt() -> None:
    try:
        while (line := input("> ")) != "q":
            run(line)
            had_error[0] = False
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
