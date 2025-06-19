from src.repositories import BaseRepository

from .models import Info, User


class UserRepository(BaseRepository):
    model = User


class InfoRepository(BaseRepository):
    model = Info
