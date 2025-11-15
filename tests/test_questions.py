import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from dateutil.parser import isoparse
from app.main import app
from app.deps import get_db

# Фикстура подменяет зависимость get_db тестовой БД
@pytest.fixture
async def override_get_db(test_db_session: AsyncSession):
    async def _override():
        yield test_db_session
    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_create_question_endpoint(override_get_db, test_client: AsyncClient):
    """
    Тест для эндпоинта создания вопроса.
    """
    payload = {"text": "Какой сегодня день?"}

    response = await test_client.post("/api/questions/", json=payload)

    assert response.status_code == 201

    data = response.json()

    # Проверка содержимого
    assert "id" in data
    assert data["text"] == payload["text"]
    assert data["answers"] == []
    assert "created_at" in data

    # id должен быть int
    assert isinstance(data["id"], int)

    # created_at должен быть валидным ISO-датой
    isoparse(data["created_at"])

@pytest.mark.asyncio
async def test_get_questions_list_endpoint(override_get_db, test_client: AsyncClient):
    # 1. Подготовка данных: создаём два вопроса через POST
    payload1 = {"text": "Первый вопрос?"}
    payload2 = {"text": "Второй вопрос?"}

    resp1 = await test_client.post("/api/questions/", json=payload1)
    resp2 = await test_client.post("/api/questions/", json=payload2)

    assert resp1.status_code == 201
    assert resp2.status_code == 201

    # 2. Делаем запрос на список вопросов
    response = await test_client.get("/api/questions/")

    assert response.status_code == 200

    data = response.json()

    # 3. Проверяем, что вернулся список
    assert isinstance(data, list)
    assert len(data) == 2

    # 4. Проверяем структуру первого элемента
    first_question = data[0]
    assert "id" in first_question
    assert "text" in first_question
    assert "created_at" in first_question
    assert "answers" in first_question

    assert first_question["text"] in {payload1["text"], payload2["text"]}
    assert isinstance(first_question["answers"], list)

    # 5. Проверяем, что created_at – валидная дата
    from dateutil.parser import isoparse
    isoparse(first_question["created_at"])

@pytest.mark.asyncio
async def test_get_answers_by_question_id(override_get_db, test_client: AsyncClient):
    # 1. Создаём вопрос
    question_payload = {"text": "Какой сегодня день?"}
    q_resp = await test_client.post("/api/questions/", json=question_payload)
    assert q_resp.status_code == 201
    created_question = q_resp.json()
    question_id = created_question["id"]

    # 2. Создаём ответы к этому вопросу
    answer_payload_1 = {
        "text": "Сегодня хороший день",
        "user_id": "user_1",
    }
    answer_payload_2 = {
        "text": "Сегодня пятница",
        "user_id": "user_2",
    }

    a_resp1 = await test_client.post(f"/api/answers/{question_id}", json=answer_payload_1)
    a_resp2 = await test_client.post(f"/api/answers/{question_id}", json=answer_payload_2)

    assert a_resp1.status_code == 201
    assert a_resp2.status_code == 201

    # 3. Получаем вопрос с ответами (успешный кейс)
    resp_ok = await test_client.get(f"/api/questions/{question_id}")
    assert resp_ok.status_code == 200

    data = resp_ok.json()

    # Проверяем вопрос
    assert data["id"] == question_id
    assert data["text"] == question_payload["text"]
    isoparse(data["created_at"])

    # Проверяем ответы
    assert "answers" in data
    answers = data["answers"]
    assert isinstance(answers, list)
    assert len(answers) == 2

    for ans in answers:
        assert ans["question_id"] == question_id
        assert "id" in ans
        assert "text" in ans
        assert "user_id" in ans
        isoparse(ans["created_at"])

    # 4. Негативный кейс — несуществующий вопрос
    non_existing_id = question_id + 1000
    resp_not_found = await test_client.get(f"/api/questions/{non_existing_id}")
    assert resp_not_found.status_code == 404
    detail = resp_not_found.json()["detail"]
    assert detail == f"Question with id {non_existing_id} not found."

@pytest.mark.asyncio
async def test_delete_question_endpoint(override_get_db, test_client: AsyncClient):
    # 1. Сначала создаём вопрос, чтобы было что удалять
    question_payload = {"text": "Вопрос для удаления"}
    create_resp = await test_client.post("/api/questions/", json=question_payload)
    assert create_resp.status_code == 201

    created_question = create_resp.json()
    question_id = created_question["id"]

    # 2. Удаляем существующий вопрос
    delete_resp = await test_client.delete(f"/api/questions/{question_id}")
    assert delete_resp.status_code == 204
    # Обычно при 204 тело пустое, можно дополнительно проверить:
    assert delete_resp.content in (b"", None)

    # 3. Проверяем, что вопрос действительно исчез:
    #    запрос по этому id должен вернуть 404
    get_resp = await test_client.get(f"/api/questions/{question_id}")
    assert get_resp.status_code == 404

    # 4. Повторная попытка удалить тот же вопрос — тоже 404
    delete_again_resp = await test_client.delete(f"/api/questions/{question_id}")
    assert delete_again_resp.status_code == 404
    data = delete_again_resp.json()
    assert data["detail"] == f"Question with id {question_id} not found."

