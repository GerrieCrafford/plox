from typing import Any, Sequence
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
from jlox.interpreter import Interpreter
from jlox.lox_function import FunctionType
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
from jlox.tokens import Token
from jlox.lox_class import ClassType
from jlox.errors import JloxRuntimeError, JloxSyntaxError


class Resolver(StmtVisitor[None], ExprVisitor[Any]):
    def __init__(self, interpreter: Interpreter) -> None:
        self._scopes: list[dict[str, bool]] = []
        self._interpreter = interpreter

        self._current_function = FunctionType.NONE
        self._current_class = ClassType.NONE

    def resolve(self, statements: Sequence[Stmt]):
        self._resolve_stmts(statements)

    def visitLiteralExpr(self, expr: LiteralExpr) -> Any:
        pass

    def visitGroupingExpr(self, expr: GroupingExpr) -> Any:
        self._resolve_expr(expr.expression)

    def visitUnaryExpr(self, expr: UnaryExpr) -> Any:
        self._resolve_expr(expr.right)

    def visitBinaryExpr(self, expr: BinaryExpr) -> Any:
        self._resolve_expr(expr.left)
        self._resolve_expr(expr.right)

    def visitAssignExpr(self, expr: "AssignExpr") -> Any:
        self._resolve_expr(expr.value)
        self._resolve_local(expr, expr.name)

    def visitExpressionStmt(self, stmt: "ExpressionStmt") -> None:
        self._resolve_expr(stmt.expression)

    def visitVariableExpr(self, expr: "VariableExpr") -> Any:
        if (
            len(self._scopes) > 0
            and self._scopes[-1].get(expr.name.lexeme, None) == False
        ):
            raise JloxSyntaxError(
                expr.name, "Can't read local variable in its own initializer."
            )

        self._resolve_local(expr, expr.name)

    def visitLogicalExpr(self, expr: "LogicalExpr") -> None:
        self._resolve_expr(expr.left)
        self._resolve_expr(expr.right)

    def visitCallExpr(self, expr: "CallExpr") -> Any:
        self._resolve_expr(expr.callee)

        for arg in expr.arguments:
            self._resolve_expr(arg)

    def visitGetExpr(self, expr: "GetExpr") -> None:
        self._resolve_expr(expr.object)

    def visitSetExpr(self, expr: "SetExpr") -> None:
        self._resolve_expr(expr.value)
        self._resolve_expr(expr.object)

    def visitThisExpr(self, expr: "ThisExpr") -> None:
        if self._current_class == ClassType.NONE:
            raise JloxSyntaxError(expr.keyword, "Can't access this outside method.")

        self._resolve_local(expr, expr.keyword)

    def visitSuperExpr(self, expr: "SuperExpr") -> None:
        match self._current_class:
            case ClassType.NONE:
                raise JloxSyntaxError(
                    expr.keyword, "Can't use 'super' outside of a class."
                )
            case ClassType.CLASS:
                raise JloxSyntaxError(
                    expr.keyword, "Can't use 'super' in a class with no superclass."
                )
            case _:
                pass

        self._resolve_local(expr, expr.keyword)

    def visitCommaExpr(self, expr: "CommaExpr") -> None:
        self._resolve_expr(expr.left)
        self._resolve_expr(expr.right)

    def visitPrintStmt(self, stmt: "PrintStmt") -> None:
        self._resolve_expr(stmt.expression)

    def visitReturnStmt(self, stmt: "ReturnStmt") -> None:
        if self._current_function == FunctionType.NONE:
            raise JloxSyntaxError(stmt.keyword, "Can't return from top-level code.")

        if stmt.value is not None:
            if self._current_function == FunctionType.INITIALIZER:
                raise JloxSyntaxError(
                    stmt.keyword, "Can't return value from class initializer."
                )

            self._resolve_expr(stmt.value)

    def visitVarStmt(self, stmt: "VarStmt") -> None:
        self._declare(stmt.name)

        if stmt.initializer is not None:
            self._resolve_expr(stmt.initializer)

        self._define(stmt.name)

    def visitBlockStmt(self, stmt: "BlockStmt") -> None:
        self._begin_scope()
        self._resolve_stmts(stmt.statements)
        self._end_scope()

    def visitIfStmt(self, stmt: "IfStmt") -> None:
        self._resolve_expr(stmt.condition)
        self._resolve_stmts([stmt.then_branch])

        if stmt.else_branch:
            self._resolve_stmts([stmt.else_branch])

    def visitWhileStmt(self, stmt: "WhileStmt") -> None:
        self._resolve_expr(stmt.condition)
        self._resolve_stmts([stmt.loop_body])

    def visitFunctionStmt(self, stmt: "FunctionStmt") -> None:
        self._declare(stmt.name)
        self._define(stmt.name)

        self._resolve_function(stmt, FunctionType.FUNCTION)

    def visitClassStmt(self, stmt: "ClassStmt") -> None:
        enclosing_class = self._current_class
        self._current_class = ClassType.CLASS

        self._declare(stmt.name)
        self._define(stmt.name)

        if stmt.superclass and stmt.name.lexeme == stmt.superclass.name.lexeme:
            raise JloxSyntaxError(
                stmt.superclass.name, "A class can't inherit from itself."
            )

        if stmt.superclass:
            self._current_class = ClassType.SUBCLASS
            self._resolve_expr(stmt.superclass)

        if stmt.superclass:
            self._begin_scope()
            self._scopes[-1]["super"] = True

        self._begin_scope()
        self._scopes[-1]["this"] = True

        for method in stmt.methods:
            ftype = (
                FunctionType.INITIALIZER
                if method.name.lexeme == "init"
                else FunctionType.METHOD
            )
            self._resolve_function(method, ftype)

        self._end_scope()

        if stmt.superclass:
            self._end_scope()

        self._current_class = enclosing_class

    def _resolve_stmts(self, stmts: Sequence[Stmt]) -> None:
        for stmt in stmts:
            stmt.accept(self)

    def _resolve_expr(self, expr: Expr) -> None:
        expr.accept(self)

    def _begin_scope(self) -> None:
        self._scopes.append({})

    def _end_scope(self) -> None:
        self._scopes.pop()

    def _declare(self, name: Token) -> None:
        if not self._scopes:
            return

        if name.lexeme in self._scopes[-1]:
            raise JloxSyntaxError(
                name, "Already a variable with this name in this scope."
            )

        self._scopes[-1][name.lexeme] = False

    def _define(self, name: Token) -> None:
        if not self._scopes:
            return

        self._scopes[-1][name.lexeme] = True

    def _resolve_local(self, expr: Expr, name: Token):
        for i, scope in enumerate(reversed(self._scopes)):
            if name.lexeme in scope:
                self._interpreter.resolve(expr, i)
                return

    def _resolve_function(self, stmt: FunctionStmt, function_type: FunctionType):
        enclosing_function = self._current_function
        self._current_function = function_type

        self._begin_scope()

        for param in stmt.params:
            self._declare(param)
            self._define(param)

        self._resolve_stmts(stmt.body)
        self._end_scope()

        self._current_function = enclosing_function
