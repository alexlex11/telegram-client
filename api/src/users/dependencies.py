from sqlalchemy.orm import Session

from .exceptions import UserDoesNotExist, UserExist
from .repositories import UserRepository


def get_user_or_404(session: Session, **filter_by):
    user_repository = UserRepository()
    user = user_repository.get(session=session, **filter_by)
    if not user:
        raise UserDoesNotExist
    return user


def check_user_exist(session: Session, **filter_by):
    user_repository = UserRepository()
    if user_repository.get(session=session, **filter_by):
        raise UserExist
