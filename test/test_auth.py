from datetime import datetime, timedelta
from unittest.mock import patch, Mock

import pytest
from fastapi import HTTPException
from jwt import PyJWTError
from pymongo.errors import DuplicateKeyError

from src.exceptions import AuthenticationError, AuthorizationError
from src.operations.auth import add_user, authenticate, resolve_user, validate_admin_user, get_current_user
from .fixtures import normal_user, normal_user_input, admin_user_input, admin_user_in


@patch('src.operations.auth.database.users')
def test_add_user_failure(mock_collection, normal_user):
    mock_collection.insert_one.side_effect = DuplicateKeyError('repeated username')

    with pytest.raises(HTTPException) as excinfo:
        add_user(normal_user)

    assert excinfo.value.status_code == 400


@patch('src.operations.auth.database.users')
@patch('src.operations.auth.password_context')
def test_add_user_success(mock_pw_ctx, mock_collection, normal_user):
    mock_pw_ctx.hash.return_value = 'myhashedpassword'
    user = add_user(normal_user)

    mock_collection.insert_one.assert_called_once_with({
        'username': normal_user.username,
        'hashed_password': 'myhashedpassword',
        'is_admin': normal_user.is_admin
    })
    assert user == normal_user


@patch('src.operations.auth.database.users')
def test_authenticate_user_not_found(mock_collection):
    form_data = Mock(username='pete', password='123')
    mock_collection.find_one.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        authenticate(form_data)

    assert excinfo.value.status_code == 401


@patch('src.operations.auth.database.users')
@patch('src.operations.auth.password_context')
def test_authenticate_wrong_password(mock_pw_ctx, mock_collection):
    form_data = Mock(username='pete', password='123')
    mock_collection.find_one.return_value = {'username': 'pete', 'is_admin': False}
    mock_pw_ctx.verify.return_value = False

    with pytest.raises(HTTPException) as excinfo:
        authenticate(form_data)

    assert excinfo.value.status_code == 401


@patch('src.operations.auth.database.users')
@patch('src.operations.auth.password_context')
@patch('src.operations.auth.encode')
def test_authenticate_success(mock_encode, mock_pw_ctx, mock_collection):
    form_data = Mock(username='pete', password='123')
    mock_collection.find_one.return_value = {'username': 'pete', 'is_admin': False}
    mock_pw_ctx.verify.return_value = True
    mock_encode.return_value = 'encodedtoken'

    token_data = authenticate(form_data)
    assert token_data == {
        'access_token': 'encodedtoken',
        'token_type': 'bearer',
        'username': 'pete'
    }


@patch('src.operations.auth.decode')
def test_resolve_user_invalid_token(mock_decode):
    mock_decode.side_effect = PyJWTError('cannot decode the thingie')

    with pytest.raises(AuthenticationError):
        resolve_user('encodedtoken')


@patch('src.operations.auth.decode')
def test_resolve_user_missing_sub(mock_decode):
    mock_decode.return_value = {'exp': datetime.utcnow() + timedelta(minutes=10)}

    with pytest.raises(AuthenticationError):
        resolve_user('encodedtoken')


@patch('src.operations.auth.database.users')
@patch('src.operations.auth.decode')
def test_resolve_user_not_found(mock_decode, mock_collection):
    mock_decode.return_value = {'sub': 'pete', 'exp': datetime.utcnow() + timedelta(minutes=10)}
    mock_collection.find_one.return_value = None

    with pytest.raises(AuthenticationError):
        resolve_user('encodedtoken')


@patch('src.operations.auth.database.users')
@patch('src.operations.auth.decode')
def test_resolve_user_success(mock_decode, mock_collection):
    mock_decode.return_value = {'sub': 'pete', 'exp': datetime.utcnow() + timedelta(minutes=10)}
    mock_collection.find_one.return_value = {'username': 'pete', 'is_admin': False}

    user = resolve_user('encodedtoken')

    assert user.username == 'pete'
    assert user.is_admin is False


def test_validate_admin_user_failure(normal_user):
    with pytest.raises(AuthorizationError):
        validate_admin_user(normal_user)


def test_validate_addmin_user_sucess(admin_user_in):
    user = validate_admin_user(admin_user_in)
    assert user.is_admin
