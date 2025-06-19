from fastapi import HTTPException, status

UserExist = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="User is already exist"
)
UserDoesNotExist = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="User is not exist"
)
