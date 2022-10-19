from jlox.tokens import Token, TokenType
from jlox.expression import (
    AssignExpr,
    BinaryExpr,
    CallExpr,
    CommaExpr,
    Expr,
    GetExpr,
    GroupingExpr,
    LiteralExpr,
    LogicalExpr,
    SetExpr,
    SuperExpr,
    ThisExpr,
    UnaryExpr,
    VariableExpr,
)
from jlox.statement import (
    ClassStmt,
    ExpressionStmt,
    FunctionStmt,
    IfStmt,
    PrintStmt,
    ReturnStmt,
    Stmt,
    VarStmt,
    BlockStmt,
    WhileStmt,
)
from jlox.errors import JloxRuntimeError, JloxSyntaxError


class Parser:
    def __init__(self, tokens: list[Token]):
        self._tokens = tokens
        self._current = 0

    def parse(self) -> list[Stmt]:
        statements: list[Stmt] = []
        while not self._is_at_end():
            statements.append(self._declaration())

        return statements

    def _declaration(self) -> Stmt:
        if self._match(TokenType.VAR):
            return self._var_declaration()
        if self._match(TokenType.CLASS):
            return self._class_declaration()
        if self._match(TokenType.FUN):
            return self._function_declaration("function")

        return self._statement()

    def _var_declaration(self) -> Stmt:
        name = self._consume(TokenType.IDENTIFIER, "Expect variable name.")

        initializer: Expr | None = None
        if self._match(TokenType.EQUAL):
            initializer = self._expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return VarStmt(name, initializer)

    def _class_declaration(self) -> ClassStmt:
        name = self._consume(TokenType.IDENTIFIER, "Expect class name.")

        superclass: VariableExpr | None = None
        if self._match(TokenType.LESS):
            identifier = self._consume(TokenType.IDENTIFIER, "Expect superclass name.")
            superclass = VariableExpr(identifier)

        self._consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")

        methods: list[FunctionStmt] = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            methods.append(self._function_declaration("method"))

        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")

        return ClassStmt(name, superclass, methods)

    def _function_declaration(self, kind: str) -> FunctionStmt:
        name = self._consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        self._consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")

        params: list[Token] = []
        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                if len(params) >= 255:
                    raise JloxRuntimeError(
                        self._peek(), "Can't have more than 255 parameters."
                    )

                params.append(
                    self._consume(TokenType.IDENTIFIER, "Expect parameter name.")
                )
                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after parameter list.")
        self._consume(TokenType.LEFT_BRACE, "Expect '{' before " + kind + " body.")

        body = self._block_statement().statements

        return FunctionStmt(name, params, body)

    def _statement(self) -> Stmt:
        if self._match(TokenType.FOR):
            return self._for_statement()
        if self._match(TokenType.IF):
            return self._if_statement()
        if self._match(TokenType.PRINT):
            return self._print_statement()
        if self._match(TokenType.RETURN):
            return self._return_statement()
        if self._match(TokenType.WHILE):
            return self._while_statement()
        if self._match(TokenType.LEFT_BRACE):
            return self._block_statement()

        return self._expression_statement()

    def _for_statement(self):
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        initializer: Stmt | None
        if self._match(TokenType.SEMICOLON):
            initializer = None
        elif self._match(TokenType.VAR):
            initializer = self._var_declaration()
        else:
            initializer = self._expression_statement()

        condition: Expr | None = None
        if not self._check(TokenType.SEMICOLON):
            condition = self._expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after 'for'.")

        increment: Expr | None = None
        if not self._check(TokenType.SEMICOLON):
            increment = self._expression()

        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        body = self._statement()

        if increment:
            body = BlockStmt([body, ExpressionStmt(increment)])

        condition = condition or LiteralExpr(True)
        body = WhileStmt(condition, body)

        if initializer:
            body = BlockStmt([initializer, body])

        return body

    def _if_statement(self) -> IfStmt:
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after 'if'.")

        then_branch = self._statement()
        else_branch: Stmt | None = None
        if self._match(TokenType.ELSE):
            else_branch = self._statement()

        return IfStmt(condition, then_branch, else_branch)

    def _print_statement(self) -> PrintStmt:
        expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return PrintStmt(expr)

    def _return_statement(self) -> ReturnStmt:
        keyword = self._previous()
        expr: Expr | None = None

        if not self._check(TokenType.SEMICOLON):
            expr = self._expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after return.")
        return ReturnStmt(keyword, expr)

    def _while_statement(self) -> WhileStmt:
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after 'while'.")

        loop_body = self._statement()

        return WhileStmt(condition, loop_body)

    def _block_statement(self) -> BlockStmt:
        statements: list[Stmt] = []

        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            statements.append(self._declaration())

        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")

        return BlockStmt(statements)

    def _expression_statement(self) -> ExpressionStmt:
        expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return ExpressionStmt(expr)

    def _expression(self) -> Expr:
        assignment = self._assignment()

        if self._match(TokenType.COMMA):
            right = self._expression()
            return CommaExpr(assignment, right)

        return assignment

    def _assignment(self) -> Expr:
        expr = self._or()

        if self._match(TokenType.EQUAL):
            equals = self._previous()
            value = self._assignment()

            if isinstance(expr, VariableExpr):
                name: Token = expr.name
                return AssignExpr(name, value)
            elif isinstance(expr, GetExpr):
                return SetExpr(expr.name, expr.object, value)

            raise JloxSyntaxError(equals, "Invalid assignment target.")

        return expr

    def _or(self) -> Expr:
        expr = self._and()

        while self._match(TokenType.OR):
            operator = self._previous()
            right = self._and()
            expr = LogicalExpr(expr, operator, right)

        return expr

    def _and(self) -> Expr:
        expr = self._equality()

        while self._match(TokenType.AND):
            operator = self._previous()
            right = self._equality()
            expr = LogicalExpr(expr, operator, right)

        return expr

    def _equality(self) -> Expr:
        expr = self._comparison()

        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self._previous()
            right = self._comparison()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def _comparison(self) -> Expr:
        expr = self._term()

        while self._match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self._previous()
            right = self._term()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def _term(self) -> Expr:
        expr = self._factor()

        while self._match(TokenType.MINUS, TokenType.PLUS):
            operator = self._previous()
            right = self._factor()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def _factor(self) -> Expr:
        expr = self._unary()

        while self._match(TokenType.SLASH, TokenType.STAR):
            operator = self._previous()
            right = self._unary()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def _unary(self) -> Expr:
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator = self._previous()
            right = self._unary()
            return UnaryExpr(operator, right)

        return self._call()

    def _call(self) -> Expr:
        expr = self._primary()

        while True:
            if self._is_at_end():
                break
            if self._match(TokenType.LEFT_PAREN):
                expr = self._finish_call(expr)
            elif self._match(TokenType.DOT):
                property = self._consume(
                    TokenType.IDENTIFIER, "Expect identifier after '.'"
                )
                expr = GetExpr(property, expr)
            else:
                break

        return expr

    def _finish_call(self, callee: Expr) -> Expr:
        arguments: list[Expr] = []

        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) > 255:
                    raise JloxSyntaxError(
                        self._peek(), "Can't have more than 255 arguments."
                    )
                arguments.append(self._or())

                if not self._match(TokenType.COMMA):
                    break

        paren = self._consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments")

        return CallExpr(callee, paren, arguments)

    def _primary(self) -> Expr:
        if self._match(TokenType.FALSE):
            return LiteralExpr(False)
        if self._match(TokenType.TRUE):
            return LiteralExpr(True)
        if self._match(TokenType.NIL):
            return LiteralExpr(None)

        if self._match(TokenType.NUMBER, TokenType.STRING):
            return LiteralExpr(self._previous().literal)

        if self._match(TokenType.LEFT_PAREN):
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expect ')' after expression")
            return GroupingExpr(expr)

        if self._match(TokenType.THIS):
            return ThisExpr(self._previous())

        if self._match(TokenType.SUPER):
            keyword = self._previous()
            self._consume(TokenType.DOT, "Expect '.' after super.")
            method = self._consume(
                TokenType.IDENTIFIER, "Expect identifier after super."
            )

            return SuperExpr(keyword, method)

        if self._match(TokenType.IDENTIFIER):
            return VariableExpr(self._previous())

        raise JloxSyntaxError(self._peek(), "Expect expression.")

    def _match(self, *args: TokenType) -> bool:
        for ttype in args:
            if self._check(ttype):
                self._advance()
                return True

        return False

    def _check(self, ttype: TokenType) -> bool:
        if self._is_at_end():
            return False

        return self._peek().type == ttype

    def _advance(self):
        if not self._is_at_end():
            self._current += 1

        return self._previous()

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        return self._tokens[self._current]

    def _previous(self) -> Token:
        return self._tokens[self._current - 1]

    def _consume(self, ttype: TokenType, msg: str):
        if self._check(ttype):
            return self._advance()

        raise JloxSyntaxError(self._peek(), msg)

    def _synchronize(self):
        self._advance()

        while not self._is_at_end():
            if self._previous().type == TokenType.SEMICOLON:
                return

            if self._peek().type in [
                TokenType.CLASS,
                TokenType.FUN,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.IF,
                TokenType.PRINT,
                TokenType.RETURN,
            ]:
                return

            self._advance()
