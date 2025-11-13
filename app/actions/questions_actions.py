from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone
from app.models import Question
from app.schemas import QuestionSchema, QuestionBaseSchema

async def create_question(question_data: QuestionBaseSchema, db: AsyncSession) -> QuestionSchema:
    """
    Создает новый вопрос.
    """
    db_question = Question(
        text=question_data.text,
        created_at=datetime.now(timezone.utc)
    )

    db.add(db_question)
    await db.commit()
    await db.refresh(db_question)

    return QuestionSchema.model_validate(db_question)

async def get_questions_list(db: AsyncSession) -> list[QuestionSchema]:
    """
    Получает список всех вопросов.
    """
    result = await db.execute(select(Question))

    questions = result.scalars().all()

    if questions is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No questions found."
        )

    return [QuestionSchema.model_validate(question) for question in questions]