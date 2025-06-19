from fastapi import APIRouter, Depends
from src.auth.dependencies import get_current_user
from src.services.ai import AIService
from src.users.models import User

from .dependencies import get_aiservice
from .schemas import SAIResponse, SUserPrompt

ai_router = APIRouter(prefix="/ai", tags=["AI requests"])


@ai_router.post(
    path="/",
    summary="Ai prompts.",
)
async def get_telethon_accounts(
    prompt: SUserPrompt,
    user: User = Depends(get_current_user),
    client: AIService = Depends(get_aiservice),
) -> SAIResponse:
    ai_responce = await client.generate_text(prompt=prompt.message)

    return SAIResponse(response=ai_responce)
