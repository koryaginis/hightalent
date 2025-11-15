from fastapi import HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from logging import Logger
from datetime import datetime, timezone
from app.schemas import AnswerSchema, AnswerBaseSchema
from app.models import Answer, Question

async def create_answer(question_id: int, answer_data: AnswerBaseSchema, db: AsyncSession, logger: Logger) -> AnswerSchema:
    """
    Создает новый ответ.
    """
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    if question is None:
        logger.warning(f"Попытка создать ответ к несуществующему вопросу id={question_id}")
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

    logger.info(
        f"Создан новый ответ с id={db_answer.id} к вопросу id={question_id} "
        f"от пользователя {answer_data.user_id}"
    )

    return AnswerSchema.model_validate(db_answer)

async def get_answer_by_id(answer_id: int, db: AsyncSession, logger: Logger) -> AnswerSchema:
    """
    Получает ответ по его id.
    """
    result = await db.execute(
    select(Answer).where(Answer.id == answer_id))
    answer = result.scalar_one_or_none()

    if answer is None:
        logger.warning(f"Попытка получить несуществующий ответ id={answer_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Answer with id {answer_id} not found."
        )
    
    logger.info(f"Получен ответ id={answer.id} к вопросу id={answer.question_id} от пользователя {answer.user_id}")

    return AnswerSchema.model_validate(answer)

async def delete_answer(answer_id: int, db: AsyncSession, logger: Logger):
    """
    Удаляет ответ по id.
    """
    result = await db.execute(
    select(Answer).where(Answer.id == answer_id))
    answer = result.scalar_one_or_none()

    if answer is None:
        logger.warning(f"Попытка удалить несуществующий ответ id={answer_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Answer with id {answer_id} not found."
        )
    
    await db.delete(answer)
    await db.commit()

    logger.info(f"Удален ответ id={answer.id} к вопросу id={answer.question_id} от пользователя {answer.user_id}")

    return {"detail": f"Answer with id {answer_id} deleted successfully."}
