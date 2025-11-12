from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class QuestionSchema(BaseModel):
    id: int = Field(description="Идентификатор вопроса")
    text: str = Field(description="Текст вопроса")
    created_at: datetime = Field(description="Время создания вопроса")

    model_config = ConfigDict(from_attributes=True)

class AnswerSchema(BaseModel):
    id: int = Field(description="Идентификатор ответа")
    question_id: int = Field(description="Идентификатор вопроса")
    text: str = Field(description="Текст ответа")
    user_id: str = Field(description="Пользователь")
    created_at: datetime = Field(description="Время создания ответа")

    model_config = ConfigDict(from_attributes=True)