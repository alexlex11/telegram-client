from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class SUserBase(BaseModel):
    username: Optional[str]


class SUserCreate(SUserBase):
    password: str
    email: EmailStr | None = None
    phone_number: str | None = None


class SUserPublic(SUserBase):
    phone_number: str | None = None
    email: EmailStr | None = None
    account_creation_date: datetime
    # chatbots: List[ChatbotPublic] = []


class SUserUpdate(SUserBase):
    phone_number: Optional[str]
    email: Optional[EmailStr]


class SUserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str
