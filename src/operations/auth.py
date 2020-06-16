from datetime import datetime, timedelta

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from jwt import encode, decode, PyJWTError
from pymongo.errors import DuplicateKeyError

from ..config import database, oauth2_scheme, password_context, \
    SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from ..exceptions import handled, ValidationError, AuthenticationError, AuthorizationError
from ..models.auth import UserIn, User


def resolve_user(token: str = Depends(oauth2_scheme)):
    user_data = None

    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')

    except PyJWTError:
        username = None

    if username:
        user_data = database.users.find_one(
            {
                'username': username
            }
        )

    if not user_data:
        raise AuthenticationError('Invalid authentication credentials.')

    return User(**user_data)


def validate_admin_user(user: User = Depends(resolve_user)):
    if not user.is_admin:
        raise AuthorizationError('User is not authorised to perform the operation.')

    return user


@handled
def add_user(user: UserIn):
    try:
        user_data = user.dict()
        user_data['hashed_password'] = password_context.hash(user_data.pop('password'))
        database.users.insert_one(user_data)

    except DuplicateKeyError:
        raise ValidationError(f'User with username {user.username} already exists.')

    return user


@handled
def authenticate(form_data: OAuth2PasswordRequestForm = Depends()):
    # Validate user exists and password matches
    user_data = database.users.find_one(
        {
            'username': form_data.username,
        }
    )
    if not (user_data and password_context.verify(form_data.password, user_data.get('hashed_password', ''))):
        raise AuthenticationError('Incorrect username or password.')

    # User+password validated, create and return token
    token_data = {
        'sub': form_data.username,
        'exp': datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    token = encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return {'access_token': token, 'token_type': 'bearer', 'username': form_data.username}


@handled
def get_current_user(user: User = Depends(resolve_user)):
    return user
