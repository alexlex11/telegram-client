from pydantic import BaseModel


class SNewMessage(BaseModel):
    chat_id: int
    bot_id: int
