from fastapi import HTTPException, status

AccountDoesNotExist = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Account does not exist"
)
