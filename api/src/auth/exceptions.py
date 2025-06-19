from fastapi import HTTPException, status

UserNotAuthorized = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="User is not authorized",
    headers={"WWW-Authenticate": "Bearer"},
)

NotValidPass = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN, detail="Password is not valid"
)

TokenTimeNotValid = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Token time is not valid"
)
TokenIdNotValid = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Token id is not valid"
)
TokenUsernameNotValid = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token username is not valid",
)
