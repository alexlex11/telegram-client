from typing import Optional

from pydantic import BaseModel


class STelethonAccount(BaseModel):
    avatar: Optional[str]
    peer: int
    username: str
    phone: str


class STelethonAccountsList(BaseModel):
    teleton_accounts: list[STelethonAccount]
