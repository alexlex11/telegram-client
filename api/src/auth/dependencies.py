from datetime import datetime, timedelta
from uuid import UUID, uuid4

from fastapi import Depends, Request, Response
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from src.config.connections import session_getter
from src.config.settings import settings
from src.users.dependencies import get_user_or_404
from src.users.models import User

from .exceptions import (
    NotValidPass,
    TokenIdNotValid,
    TokenTimeNotValid,
    TokenUsernameNotValid,
    UserNotAuthorized,
)
from .repositories import PasswordRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_pass, hashed_pass) -> bool:
    return pwd_context.verify(plain_pass, hashed_pass)


def save_password(session: Session, password: str) -> UUID:
    hashed_pass = get_password_hash(password)
    pass_id = uuid4()
    pas_repository = PasswordRepository()
    pas_repository.add(session=session, id=pass_id, hashed_pass=hashed_pass)
    return pass_id


def check_password(plain_pass, hashed_pass):
    password_is_valid = verify_password(plain_pass, hashed_pass)
    if not password_is_valid:
        raise NotValidPass


def get_user_pass(session: Session, user: User) -> str:
    pas_repository = PasswordRepository()
    password = pas_repository.get(session=session, id=user.password_id)
    return password.hashed_pass


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret,
        settings.hash,
    )

    return encoded_jwt


def check_access_token(payload: dict):
    expire = payload.get("exp")
    if not expire or int(expire) < datetime.utcnow().timestamp():
        raise TokenTimeNotValid

    user_id = payload.get("sub")
    if not user_id:
        raise TokenIdNotValid

    username = payload.get("username")
    if not username:
        raise TokenUsernameNotValid


def get_token(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        authorization_header = request.headers.get("Authorization")

        if authorization_header:
            try:
                # Ожидаем формат "Bearer <token>"
                token_type, token = authorization_header.split(" ", 1)
                if token_type.lower() != "bearer":
                    raise UserNotAuthorized  # Или другая ошибка, если токен не Bearer
            except ValueError:
                raise UserNotAuthorized  # Неправильный формат заголовка Authorization
        else:
            # 3. Если токен не найден ни там, ни там, выбрасываем исключение
            raise UserNotAuthorized

    return token


def set_token(response: Response, user_id: UUID, username: str):
    user_id = str(user_id)
    access_token = create_access_token({"sub": user_id, "username": username})
    response.set_cookie("access_token", access_token, httponly=True)
    return access_token


def get_current_user(
    token: str = Depends(get_token),
    session: Session = Depends(session_getter),
):
    try:
        payload = jwt.decode(
            token,
            settings.secret,
            settings.hash,
        )
    except JWTError:
        raise UserNotAuthorized

    check_access_token(payload)

    user = get_user_or_404(session, username=payload.get("username"))

    return user
