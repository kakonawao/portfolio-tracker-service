from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class UserBase(BaseModel):
    username: str
    is_admin: bool = False


class UserIn(UserBase):
    password: str
    # TODO: add field base_currency when Currency model is added


class User(UserBase):
    pass
    # TODO: add field base_currency when Currency model is added
