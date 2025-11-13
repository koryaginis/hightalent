from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class QuestionBaseSchema(BaseModel):
    text: str = Field(description="Текст вопроса")

    model_config = ConfigDict(from_attributes=True)

class QuestionSchema(QuestionBaseSchema):
    id: int = Field(description="Идентификатор вопроса")
    created_at: datetime = Field(description="Время создания вопроса")

class AnswerBaseSchema(BaseModel):
    text: str = Field(description="Текст ответа")
    user_id: str = Field(description="Пользователь")

    model_config = ConfigDict(from_attributes=True)

class AnswerSchema(AnswerBaseSchema):
    id: int = Field(description="Идентификатор ответа")
    question_id: int = Field(description="Идентификатор вопроса")
    created_at: datetime = Field(description="Время создания ответа")