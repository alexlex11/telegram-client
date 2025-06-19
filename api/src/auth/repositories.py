from src.repositories import BaseRepository

from .models import Password


class PasswordRepository(BaseRepository):
    model = Password
