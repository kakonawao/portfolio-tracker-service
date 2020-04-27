import pytest
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError
from unittest.mock import patch

from src.operations.auth import add_user
from .fixtures import normal_user_in, normal_user_input


@patch('src.operations.auth.database.users')
def test_add_user_success(mock_collection, normal_user_in):
    res = add_user(normal_user_in)

    mock_collection.insert_one.assert_called_once_with({
        'username': normal_user_in.username,
        'password': normal_user_in.password,
        'is_admin': normal_user_in.is_admin
    })
    assert res == normal_user_in


@patch('src.operations.auth.database.users')
def test_add_user_failure(mock_collection, normal_user_in):
    mock_collection.insert_one.side_effect = DuplicateKeyError('repeated username')
    with pytest.raises(HTTPException):
        add_user(normal_user_in)
