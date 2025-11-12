from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import QuestionSchema, QuestionBaseSchema
from app.deps import get_db
from app.actions.questions_actions import (
    create_question
)

router = APIRouter(
    prefix="/questions",
    tags=["Questions"],
)

@router.post("/", response_model=QuestionSchema, status_code=status.HTTP_201_CREATED)
async def create_question_endpoint(
    question_data: QuestionBaseSchema,
    db: AsyncSession = Depends(get_db)
):
    """
    Эндпоинт для создания нового вопроса.
    """
    return await create_question(question_data=question_data, db=db)

# @router.get("/get-by-status/{status}", response_model=List[IncidentSchema], status_code=status.HTTP_200_OK)
# async def get_incidents_by_status_endpoint(
#     incident_status: StatusSchema,
#     db: AsyncSession = Depends(get_db)
# ):
#     """
#     Эндпоинт для получения инцидентов с указанным статусом.

#         Статусы:
#         - "OPENED": Создан
#         - "IN_PROGRESS": В работе
#         - "RESOLVED: Проблема устранена
#         - "CLOSED": Закрыт

#         Источники инцидента:
#         - "OPERATOR": Сообщение от оператора
#         - "MONITORING": Система мониторинга
#         - "PARTNER": Партнер / сторонняя компания
#         - "USER": Пользователь приложения
#         - "MANUAL": Ручной ввод админом

#     """
#     return await get_incidents_by_status(incident_status=incident_status, db=db)

# @router.put("/update/{incident_id}", response_model=IncidentSchema, status_code=status.HTTP_200_OK)
# async def update_incident_endpoint(
#     incident_id: PositiveInt,
#     update_data: IncidentUpdateSchema,
#     db: AsyncSession = Depends(get_db)
# ):
#     """
#     Эндпоинт для обновления инцидента по id.

#         Статусы:
#         - "OPENED": Создан
#         - "IN_PROGRESS": В работе
#         - "RESOLVED: Проблема устранена
#         - "CLOSED": Закрыт

#         Источники инцидента:
#         - "OPERATOR": Сообщение от оператора
#         - "MONITORING": Система мониторинга
#         - "PARTNER": Партнер / сторонняя компания
#         - "USER": Пользователь приложения
#         - "MANUAL": Ручной ввод админом
        
#     """
#     return await update_incident(incident_id=incident_id, update_data=update_data, db=db)
