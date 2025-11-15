from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from logging import Logger
from datetime import datetime, timezone
from app.models import Question
from app.schemas import QuestionSchema, QuestionBaseSchema

async def create_question(question_data: QuestionBaseSchema, db: AsyncSession, logger: Logger) -> QuestionSchema:
    """
    Создает новый вопрос.
    """
    db_question = Question(
        text=question_data.text,
        created_at=datetime.now(timezone.utc)
    )

    db.add(db_question)
    await db.commit()
    await db.refresh(db_question, attribute_names=['answers'])

    logger.info(
        f"Создан новый вопрос: id={db_question.id}, "
        f"text='{db_question.text[:50]}', "
        f"created_at={db_question.created_at.isoformat()}"
    )

    return QuestionSchema.model_validate(db_question)

async def get_questions_list(db: AsyncSession, logger: Logger) -> list[QuestionSchema]:
    """
    Получает список всех вопросов.
    """
    result = await db.execute(select(Question).options(selectinload(Question.answers)))

    questions = result.scalars().all()

    logger.info(f"Получено {len(questions)} вопросов из базы")

    if questions is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No questions found."
        )

    return [QuestionSchema.model_validate(question) for question in questions]

async def get_answers_by_question_id(question_id: int, db: AsyncSession, logger: Logger) -> QuestionSchema:
    """
    Получает вопрос и все ответы на него по его id.
    """
    result = await db.execute(
        select(Question)
        .options(selectinload(Question.answers))
        .where(Question.id == question_id)
    )
    question = result.scalar_one_or_none()

    if question is None:
        logger.warning(f"Вопрос с id {question_id} не найден")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with id {question_id} not found."
        )
    
    logger.info(f"Получен вопрос id {question.id} с {len(question.answers)} ответ(ами)")

    return QuestionSchema.model_validate(question)

async def delete_question(question_id: int, db: AsyncSession, logger: Logger):
    """
    Удаляет вопрос и все ответы на него по id.
    """
    result = await db.execute(
    select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()

    if question is None:
        logger.warning(f"Попытка удалить несуществующий вопрос с id {question_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with id {question_id} not found."
        )
    
    await db.delete(question)
    await db.commit()

    logger.info(f"Вопрос с id {question_id} и все ответы успешно удалены")

    return {"detail": f"Answer with id {question_id} deleted successfully."}