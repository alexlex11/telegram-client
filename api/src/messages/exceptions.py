from fastapi import HTTPException, status

CannotGetMessages = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Cannot fetch messages, invalid input",
)
