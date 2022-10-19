from typing import Any
from jlox.environment import Environment
from jlox.expression import (
    AssignExpr,
    BinaryExpr,
    CallExpr,
    CommaExpr,
    Expr,
    ExprVisitor,
    GroupingExpr,
    LiteralExpr,
    LogicalExpr,
    SetExpr,
    SuperExpr,
    ThisExpr,
    UnaryExpr,
    VariableExpr,
    GetExpr,
)
from jlox.lox_class import LoxClass
from jlox.lox_function import LoxFunction
from jlox.lox_instance import LoxInstance
from jlox.tokens import Token, TokenType
from jlox.statement import (
    ClassStmt,
    FunctionStmt,
    ReturnStmt,
    Stmt,
    StmtVisitor,
    ExpressionStmt,
    PrintStmt,
    VarStmt,
    BlockStmt,
    IfStmt,
    WhileStmt,
)
from jlox.errors import JloxRuntimeError
from jlox.lox_callable import LoxCallable
from jlox.native_functions import AssertEqualFunc, ClockFunc
from jlox.return_wrapper import ReturnWrapper


def super_token():
    return Token(TokenType.SUPER, "super", None, 0)


def this_token():
    return Token(TokenType.THIS, "this", None, 0)


class Interpreter(ExprVisitor[Any], StmtVisitor[None]):
    def __init__(self):
        self._globals = Environment()
        self._environment = self._globals

        self._globals.define("clock", ClockFunc())
        self._globals.define("assert_equal", AssertEqualFunc())

        self._locals: dict[Expr, int] = {}

    @property
    def globals(self) -> Environment:
        return self._globals

    def interpret(self, statements: list[Stmt]):
        for stmt in statements:
            self._execute(stmt)

    def visitLiteralExpr(self, expr: LiteralExpr) -> Any:
        return expr.value

    def visitGroupingExpr(self, expr: GroupingExpr) -> Any:
        return self._evaluate(expr.expression)

    def visitUnaryExpr(self, expr: UnaryExpr) -> Any:
        right = self._evaluate(expr.right)

        match expr.operator.type:
            case TokenType.MINUS:
                self._check_number_operands(expr.operator, right)
                return -float(right)
            case TokenType.BANG:
                return not self._is_truthy(right)
            case _:
                return None

    def visitBinaryExpr(self, expr: BinaryExpr) -> Any:
        left = self._evaluate(expr.left)
        right = self._evaluate(expr.right)

        match (expr.operator.type, left, right):
            case TokenType.MINUS, float(l) | int(l), float(r) | int(r):
                return l - r
            case TokenType.SLASH, float(l) | int(l), float(r) | int(r):
                return l / r
            case TokenType.STAR, float(l) | int(l), float(r) | int(r):
                return l * r
            case TokenType.PLUS, float(l) | int(l), float(r) | int(r):
                return l + r
            case TokenType.PLUS, str(l), str(r):
                return l + r
            case TokenType.GREATER, float(l) | int(l), float(r) | int(r):
                return l > r
            case TokenType.GREATER_EQUAL, float(l) | int(l), float(r) | int(r):
                return l >= r
            case TokenType.LESS, float(l) | int(l), float(r) | int(r):
                return l < r
            case TokenType.LESS_EQUAL, float(l) | int(l), float(r) | int(r):
                return l <= r
            case TokenType.BANG_EQUAL, l, r:
                return l != r
            case TokenType.EQUAL_EQUAL, l, r:
                return l == r
            case tt, _, _:
                if tt in [
                    TokenType.MINUS,
                    TokenType.SLASH,
                    TokenType.STAR,
                    TokenType.GREATER,
                    TokenType.GREATER_EQUAL,
                    TokenType.LESS,
                    TokenType.LESS_EQUAL,
                ]:
                    raise JloxRuntimeError(
                        expr.operator, "Operands must be two numbers"
                    )

                if tt == TokenType.PLUS:
                    raise JloxRuntimeError(
                        expr.operator, "Operands must be two numbers or two strings"
                    )

                return None
            case _:
                return None

    def visitAssignExpr(self, expr: "AssignExpr") -> Any:
        value = self._evaluate(expr.value)

        dist = self._locals.get(expr, None)
        if dist is not None:
            self._environment.assign_at(dist, expr.name, value)
        else:
            self._globals.assign(expr.name, value)

        return value

    def visitExpressionStmt(self, stmt: "ExpressionStmt") -> None:
        self._evaluate(stmt.expression)

    def visitVariableExpr(self, expr: "VariableExpr") -> Any:
        return self._lookup_var(expr.name, expr)

    def visitLogicalExpr(self, expr: "LogicalExpr") -> Expr:
        left = self._evaluate(expr.left)

        if expr.operator.type == TokenType.OR:
            if left:
                return left
        else:
            if not left:
                return left

        return self._evaluate(expr.right)

    def visitGetExpr(self, expr: "GetExpr") -> Expr:
        obj = self._evaluate(expr.object)

        if not isinstance(obj, LoxInstance):
            raise JloxRuntimeError(expr.name, "Only instances have properties.")

        return obj.get(expr.name)

    def visitSetExpr(self, expr: "SetExpr") -> Any:
        obj = self._evaluate(expr.object)

        if not isinstance(obj, LoxInstance):
            raise JloxRuntimeError(expr.name, "Only instances have properties.")

        val = self._evaluate(expr.value)
        obj.set(expr.name, val)
        return val

    def visitThisExpr(self, expr: "ThisExpr") -> Any:
        return self._lookup_var(expr.keyword, expr)

    def visitSuperExpr(self, expr: "SuperExpr") -> LoxFunction:
        dist = self._locals.get(expr)
        assert dist is not None

        superclass: LoxClass = self._environment.get_at(dist, super_token())
        object: LoxInstance = self._environment.get_at(dist - 1, this_token())

        method = superclass.find_method(expr.method.lexeme)
        if not method:
            raise RuntimeError(expr.method, f"Undefined property {expr.method.lexeme}.")

        return method.bind(object)

    def visitCallExpr(self, expr: "CallExpr") -> Any:
        callee = self._evaluate(expr.callee)

        if not isinstance(callee, LoxCallable):
            raise JloxRuntimeError(expr.paren, "Can only call functions and classes.")

        arguments = [self._evaluate(arg) for arg in expr.arguments]

        if len(arguments) != callee.arity:
            raise JloxRuntimeError(
                expr.paren,
                f"Expected {callee.arity} arguments but got {len(arguments)}.",
            )

        return callee.call(self, arguments)

    def visitCommaExpr(self, expr: "CommaExpr") -> Any:
        _, right = self._evaluate(expr.left), self._evaluate(expr.right)
        return right

    def visitPrintStmt(self, stmt: "PrintStmt") -> None:
        value = self._evaluate(stmt.expression)
        print(value)

    def visitReturnStmt(self, stmt: "ReturnStmt") -> None:
        value = self._evaluate(stmt.value) if stmt.value is not None else None

        raise ReturnWrapper(value)

    def visitVarStmt(self, stmt: "VarStmt") -> None:
        value = self._evaluate(stmt.initializer) if stmt.initializer else None

        self._environment.define(stmt.name.lexeme, value)

    def visitBlockStmt(self, stmt: "BlockStmt") -> None:
        self._executeBlock(stmt.statements, Environment(self._environment))

    def visitIfStmt(self, stmt: "IfStmt") -> None:
        if self._evaluate(stmt.condition):
            self._execute(stmt.then_branch)
        elif stmt.else_branch:
            self._execute(stmt.else_branch)

    def visitWhileStmt(self, stmt: "WhileStmt") -> None:
        while self._evaluate(stmt.condition):
            self._execute(stmt.loop_body)

    def visitFunctionStmt(self, stmt: "FunctionStmt") -> None:
        func = LoxFunction(stmt, self._environment)
        self._environment.define(stmt.name.lexeme, func)

    def visitClassStmt(self, stmt: "ClassStmt") -> None:
        superclass = None
        if stmt.superclass:
            superclass = self._evaluate(stmt.superclass)
            if not isinstance(superclass, LoxClass):
                raise RuntimeError(stmt.superclass.name, "Superclass must be a class.")

        self._environment.define(stmt.name.lexeme, None)

        if stmt.superclass:
            self._environment = Environment(self._environment)
            self._environment.define("super", superclass)

        methods: dict[str, LoxFunction] = {}
        for method in stmt.methods:
            function = LoxFunction(
                method, self._environment, method.name.lexeme == "init"
            )
            methods[method.name.lexeme] = function

        lox_class = LoxClass(stmt.name.lexeme, superclass, methods)

        if superclass:
            assert self._environment.enclosing is not None
            self._environment = self._environment.enclosing

        self._environment.assign(stmt.name, lox_class)

    def resolve(self, expr: Expr, depth: int):
        self._locals[expr] = depth

    def _evaluate(self, expr: Expr) -> Any:
        return expr.accept(self)

    def _execute(self, stmt: Stmt):
        stmt.accept(self)

    def _executeBlock(self, statements: list[Stmt], env: Environment):
        prev_env = self._environment

        try:
            self._environment = env

            for statement in statements:
                self._execute(statement)
        finally:
            self._environment = prev_env

    def _is_truthy(self, val: Any) -> bool:
        return bool(val)

    def _check_number_operands(self, operator: Token, *operands: Any):
        if all(isinstance(operand, float) for operand in operands):
            return

        if len(operands) == 1:
            raise JloxRuntimeError(operator, "Operand must be a number.")
        else:
            raise JloxRuntimeError(operator, "Operands must be numbers.")

    def _lookup_var(self, name: Token, expr: Expr):
        dist = self._locals.get(expr, None)
        if dist is not None:
            return self._environment.get_at(dist, name)
        else:
            return self._globals.get(name)
