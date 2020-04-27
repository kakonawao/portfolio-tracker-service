from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pymongo import MongoClient


# Database configuration

DB = {
    'auth': {
        'username': 'service-portfolio',
        'password': 'gRWn33ZIhV9u'
    },
    'connection': {
        'schema': 'mongodb+srv',
        'host': 'cluster0-ind5n.mongodb.net',
        'path': 'test?retryWrites=true&w=majority'
    }
}

CONNECTION_STRING = '{schema}://{username}:{password}@{host}/{path}'.format(**DB['auth'], **DB['connection'])

database = MongoClient(CONNECTION_STRING).portfolio


# Auth configuration

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/sessions')
password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
