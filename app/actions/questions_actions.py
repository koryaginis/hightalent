from sqlalchemy.ext.asyncio import AsyncSession
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