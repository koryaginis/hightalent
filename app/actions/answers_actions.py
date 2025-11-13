from fastapi import HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from app.schemas import AnswerSchema, AnswerBaseSchema, QuestionSchema
from app.models import Answer, Question

async def create_answer(question_id: int, answer_data: AnswerBaseSchema, db: AsyncSession) -> AnswerSchema:
    """
    Создает новый ответ.
    """
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Question with id {question_id} does not exist."
        )

    db_answer = Answer(
        question_id=question_id,
        text=answer_data.text,
        user_id=answer_data.user_id,
        created_at=datetime.now(timezone.utc).replace(tzinfo=None)
    )

    db.add(db_answer)
    await db.commit()
    await db.refresh(db_answer)

    return AnswerSchema.model_validate(db_answer)

async def get_answer_by_id(answer_id: int, db: AsyncSession) -> AnswerSchema:
    """
    Получает ответ по его id.
    """
    result = await db.execute(
    select(Answer).where(Answer.id == answer_id))
    answer = result.scalar_one_or_none()

    if answer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Answer with id {answer_id} not found."
        )

    return AnswerSchema.model_validate(answer)
