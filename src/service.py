from fastapi import FastAPI

from .config import database
from .models.auth import User
from .models.core import Institution
from .operations.auth import add_user, authenticate, get_current_user
from .operations.core import add_institution


# Service

service = FastAPI()


# Start/end event hooks

@service.on_event("startup")
async def startup_event():
    database.users.create_index('username', unique=True)


# Hook up resources to operations

service.post('/users', response_model=User)(add_user)
service.post('/sessions')(authenticate)
service.get('/sessions/current', response_model=User)(get_current_user)

service.post('/institutions', response_model=Institution)(add_institution)
