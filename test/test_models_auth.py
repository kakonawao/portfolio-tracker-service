import pytest
from pydantic import ValidationError

from src.models.auth import UserIn
from .fixtures import normal_user_input


def test_invalid_user():
    with pytest.raises(ValidationError):
        UserIn()


def test_valid_user(normal_user_input):
    user = UserIn(**normal_user_input)

    assert user.username == normal_user_input['username']
    assert user.password == normal_user_input['password']
    assert user.is_admin is False
