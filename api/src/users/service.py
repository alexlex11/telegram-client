from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session
from src.auth.dependencies import check_password, get_user_pass, save_password

from .dependencies import check_user_exist, get_user_or_404
from .models import Info, User
from .repositories import InfoRepository, UserRepository


class UserService:
    @classmethod
    def create(
        cls, session: Session, username: str, password: str, **extra_data
    ) -> User:
        check_user_exist(session, username=username)
        pass_id = save_password(session, password)
        user_repository = UserRepository()
        user = user_repository.add(
            session=session, username=username, password_id=pass_id
        )
        info_repository = InfoRepository()
        info_repository.add(session=session, user_id=user.id, **extra_data)
        return user

    @classmethod
    def login(cls, session: Session, username: str, password: str) -> User:
        user = get_user_or_404(session, username=username)
        hashed_pass = get_user_pass(session, user)
        check_password(password, hashed_pass)
        return user


class UserInfoService:
    def __init__(self, session: Session):
        self.info_repository = InfoRepository()
        self.session = session

    def get_user_info(self, user_id: UUID) -> Optional[Info]:
        user_info = self.info_repository.get(self.session, user_id=user_id)

        return user_info
