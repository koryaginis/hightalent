from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from logging import Logger
from app.schemas import QuestionSchema, QuestionBaseSchema
from app.deps import get_db, get_logger
from app.actions.questions_actions import (
    create_question,
    get_questions_list,
    get_answers_by_question_id,
    delete_question
)

router = APIRouter(
    prefix="/questions",
    tags=["Questions"],
)

@router.post("/", response_model=QuestionSchema, status_code=status.HTTP_201_CREATED)
async def create_question_endpoint(
    question_data: QuestionBaseSchema,
    db: AsyncSession = Depends(get_db),
    logger: Logger = Depends(get_logger)
):
    """
    Эндпоинт для создания нового вопроса.
    """
    return await create_question(question_data=question_data, db=db, logger=logger)

@router.get("/", response_model=List[QuestionSchema], status_code=status.HTTP_200_OK)
async def get_questions_list_endpoint(
    db: AsyncSession = Depends(get_db),
    logger: Logger = Depends(get_logger)
):
    """
    Эндпоинт для получения всех вопросов.
    """
    return await get_questions_list(db=db, logger=logger)

@router.get("/{question_id}", response_model=QuestionSchema, status_code=status.HTTP_200_OK)
async def get_answers_by_question_id_endpoint(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    logger: Logger = Depends(get_logger)
):
    """
    Эндпоинт для получения вопроса и всех ответов на него.
    """
    return await get_answers_by_question_id(question_id=question_id, db=db, logger=logger)

@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question_endpoint(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    logger: Logger = Depends(get_logger)
):
    """
    Эндпоинт для удаления вопроса и ответов на него по id.
    """
    return await delete_question(question_id=question_id, db=db, logger=logger)
