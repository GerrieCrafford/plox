from jlox.tokens import Token, TokenType
from jlox.expression import AssignExpr, BinaryExpr, Expr, GroupingExpr, LiteralExpr, UnaryExpr, VariableExpr
from jlox.statement import ExpressionStmt, PrintStmt, Stmt, VarStmt
from jlox.errors import JloxSyntaxError


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
        
        return self._statement()
    
    def _var_declaration(self) -> Stmt:
        name = self._consume(TokenType.IDENTIFIER, 'Expect variable name.')

        initializer: Expr | None = None
        if self._match(TokenType.EQUAL):
            initializer = self._expression()
        
        self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return VarStmt(name, initializer)
    
    def _statement(self) -> Stmt:
        if self._match(TokenType.PRINT):
            return self._print_statement()
        
        return self._expression_statement()
    
    def _print_statement(self) -> PrintStmt:
        expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return PrintStmt(expr)
    
    def _expression_statement(self) -> ExpressionStmt:
        expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return ExpressionStmt(expr)

    def _expression(self) -> Expr:
        return self._assignment()
    
    def _assignment(self) -> Expr:
        expr = self._equality()

        if self._match(TokenType.EQUAL):
            equals = self._previous()
            value = self._assignment()

            if isinstance(expr, VariableExpr):
                name: Token = expr.name
                return AssignExpr(name, value)
            
            raise JloxSyntaxError(equals, "Invalid assignment target.")
        
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

        return self._primary()

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
