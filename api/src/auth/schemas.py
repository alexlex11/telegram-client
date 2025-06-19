from datetime import datetime

from pydantic import UUID4, BaseModel


class SUserDisplay(BaseModel):
    id: UUID4
    username: str
    password_id: UUID4
    created_at: datetime


class SUserAuth(BaseModel):
    username: str
    password: str


class SRegistration(BaseModel):
    token: str
    user: SUserDisplay


class SLogin(BaseModel):
    token: str
    user: SUserDisplay
