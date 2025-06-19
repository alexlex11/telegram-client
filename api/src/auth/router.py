from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from src.config.connections import session_getter
from src.users.models import User
from src.users.service import UserService

from .dependencies import get_current_user, set_token
from .schemas import SLogin, SRegistration, SUserAuth

auth_router = APIRouter(prefix="/auth", tags=["Authorization"])


@auth_router.post(
    path="/register",
    status_code=status.HTTP_201_CREATED,
    summary="Endpoint for register user",
)
def register_user(
    response: Response,
    user_data: SUserAuth,
    session: Session = Depends(session_getter),
) -> SRegistration:
    """Endpoint for user registration. Returns a JWT and user data after successful
    registration and stores a cookie with that JWT.

    Possible status codes:
    1) 201 - user successfully registered
    2) 400 - user with such username already exist
    """
    user = UserService.create(
        session=session,
        username=user_data.username,
        password=user_data.password,
    )
    access_token = set_token(response, user.id, user.username)

    session.commit()

    return {"token": access_token, "user": user}


@auth_router.post(path="/login", summary="Endpoint for login user")
def login_user(
    response: Response,
    user_data: SUserAuth,
    session: Session = Depends(session_getter),
) -> SLogin:
    """Endpoint for user login. Returns a JWT and user data after successful
    registration and stores a cookie with that JWT.

    Possible status codes:
    1) 200 - user successfully login
    2) 403 - password is not valid
    3) 404 - user with such username does not exist
    """
    user = UserService.login(
        session=session,
        username=user_data.username,
        password=user_data.password,
    )
    access_token = set_token(response, user.id, user.username)

    return {"token": access_token, "user": user}


@auth_router.delete(path="/logout", summary="Endpoint for user logout")
def logout_user(
    response: Response,
    user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Endpoint for user logout. Delete JWT token from users cookie.

    Possible status codes:
    1) 200 - user successfully logout
    2) 401 - user unauthorized (bad JWT data)
    """
    response.delete_cookie("access_token")

    return {"message": "Access is denied"}
