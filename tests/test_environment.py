import pytest

from jlox.environment import Environment
from jlox.errors import JloxRuntimeError
from jlox.tokens import Token, TokenType


@pytest.fixture
def env():
    return Environment()


def create_token(name: str) -> Token:
    return Token(TokenType.IDENTIFIER, name, None, 1)


def test_error_on_undefined_access(env: Environment):
    var = create_token("some_var")
    with pytest.raises(JloxRuntimeError):
        env.get(var)

    with pytest.raises(JloxRuntimeError):
        env.assign(var, 5)


def test_definition_assignment_retrieval(env: Environment):
    var = create_token("another_var")
    env.define(var.lexeme, 10)
    assert env.get(var) == 10

    env.assign(var, "some value")
    assert env.get(var) == "some value"


def test_nesting_environments():
    env_parent = Environment()
    env_child = Environment(env_parent)

    child_var = create_token("child_var")
    parent_var = create_token("parent_var")

    env_child.define(child_var.lexeme, 1)
    env_parent.define(parent_var.lexeme, "value")

    assert env_child.get(child_var) == 1
    assert env_child.get(parent_var) == "value"
    assert env_parent.get(parent_var) == "value"

    with pytest.raises(JloxRuntimeError):
        env_parent.get(child_var)
