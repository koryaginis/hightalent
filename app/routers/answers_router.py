from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_db
from app.schemas import AnswerSchema, AnswerBaseSchema
from app.actions.answers_actions import (
    create_answer
)

router = APIRouter(
    prefix="/answers",
    tags=["Answers"],
)

@router.post("/{question_id}", response_model=AnswerSchema, status_code=status.HTTP_201_CREATED)
async def create_answer_endpoint(
    question_id: int,
    answer_data: AnswerBaseSchema,
    db: AsyncSession = Depends(get_db)
):
    """
    Эндпоинт для создания нового ответа.
    """
    return await create_answer(question_id=question_id, answer_data=answer_data, db=db)