from pydantic import BaseModel


class SUserPrompt(BaseModel):
    message: str


class SAIResponse(BaseModel):
    response: str
