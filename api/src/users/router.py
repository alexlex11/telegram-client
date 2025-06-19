import logging

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session, joinedload
from src.auth.dependencies import get_current_user, get_password_hash, verify_password
from src.config.connections import session_getter

from .models import User
from .schemas import SUserPasswordUpdate, SUserPublic, SUserUpdate
from .service import UserInfoService

logger = logging.getLogger(__name__)

user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.get(path="/me", summary="Endpoint for getting current user info")
def get_me(
    response: Response,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(session_getter),
) -> SUserPublic:
    info_service = UserInfoService(session=session)
    user_info = info_service.get_user_info(user_id=current_user.id)

    user_public = SUserPublic(
        id=current_user.id,
        username=current_user.username,
        email=user_info.email,
        phone_number=user_info.phone_number,
        account_creation_date=current_user.created_at,
    )

    return user_public


@user_router.patch(path="/me", summary="Endpoint for patch user info.")
def update_user(
    response: Response,
    user_data: SUserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(session_getter),
) -> Response:

    info_service = UserInfoService(session=session)
    user_info = info_service.get_user_info(user_id=current_user.id)

    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User info not found.",
        )

    try:
        if user_data.email is not None:
            user_info.email = user_data.email

        if user_data.phone_number is not None:
            user_info.phone_number = user_data.phone_number

        if user_data.username is not None:
            current_user.username = user_data.username

        session.add(user_info)
        session.add(current_user)
        session.commit()
        session.refresh(user_info)
        session.refresh(current_user)
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {e}",
        )

    response.status_code = status.HTTP_204_NO_CONTENT

    return response


@user_router.patch(path="/me/password")
def update_current_user_password(
    response: Response,
    user_data: SUserPasswordUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(session_getter),
) -> Response:
    db_user = (
        session.query(User)
        .options(joinedload(User.password))
        .filter(User.id == current_user.id)
        .first()
    )

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден в базе данных",
        )

    if not db_user.password:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Паспорт пользователя не найден",
        )

    # Проверка старого пароля
    if not verify_password(user_data.old_password, db_user.password.hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный старый пароль",
        )

    # Обновление пароля
    db_user.password.hashed_pass = get_password_hash(user_data.new_password)
    session.commit()
    session.refresh(db_user)

    response.status_code = status.HTTP_204_NO_CONTENT

    return response
