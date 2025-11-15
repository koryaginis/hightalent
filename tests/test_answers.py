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
async def test_create_answer_endpoint(override_get_db, test_client: AsyncClient):
    # 1. Сначала создаём вопрос, чтобы было к чему привязывать ответ
    question_payload = {"text": "Какой сегодня день?"}
    q_resp = await test_client.post("/api/questions/", json=question_payload)
    assert q_resp.status_code == 201

    created_question = q_resp.json()
    question_id = created_question["id"]

    # 2. Успешное создание ответа к существующему вопросу
    answer_payload = {
        "text": "Сегодня хороший день",
        "user_id": "user_1",
    }

    a_resp = await test_client.post(f"/api/answers/{question_id}", json=answer_payload)
    assert a_resp.status_code == 201

    data = a_resp.json()

    # Проверяем структуру и данные
    assert "id" in data
    assert data["question_id"] == question_id
    assert data["text"] == answer_payload["text"]
    assert data["user_id"] == answer_payload["user_id"]
    assert "created_at" in data
    isoparse(data["created_at"])

    # 3. Негативный кейс: создаём ответ к несуществующему вопросу
    non_existing_id = question_id + 1000

    a_resp_bad = await test_client.post(
        f"/api/answers/{non_existing_id}",
        json=answer_payload,
    )

    assert a_resp_bad.status_code == 400
    error_data = a_resp_bad.json()
    assert error_data["detail"] == f"Question with id {non_existing_id} does not exist."

@pytest.mark.asyncio
async def test_get_answer_by_id_endpoint(override_get_db, test_client: AsyncClient):
    # 1. Создаём вопрос, чтобы было к чему привязать ответ
    question_payload = {"text": "Какой сегодня день?"}
    q_resp = await test_client.post("/api/questions/", json=question_payload)
    assert q_resp.status_code == 201

    created_question = q_resp.json()
    question_id = created_question["id"]

    # 2. Создаём ответ к этому вопросу
    answer_payload = {
        "text": "Сегодня хороший день",
        "user_id": "user_1",
    }

    create_answer_resp = await test_client.post(
        f"/api/answers/{question_id}",
        json=answer_payload,
    )
    assert create_answer_resp.status_code == 201

    created_answer = create_answer_resp.json()
    answer_id = created_answer["id"]

    # 3. Успешно получаем ответ по его id
    get_resp = await test_client.get(f"/api/answers/{answer_id}")
    assert get_resp.status_code == 200

    data = get_resp.json()

    # Проверяем структуру и данные
    assert data["id"] == answer_id
    assert data["question_id"] == question_id
    assert data["text"] == answer_payload["text"]
    assert data["user_id"] == answer_payload["user_id"]
    assert "created_at" in data
    isoparse(data["created_at"])

    # 4. Негативный кейс: ответ с несуществующим id
    non_existing_id = answer_id + 1000

    not_found_resp = await test_client.get(f"/api/answers/{non_existing_id}")
    assert not_found_resp.status_code == 404

    error_data = not_found_resp.json()
    assert error_data["detail"] == f"Answer with id {non_existing_id} not found."

@pytest.mark.asyncio
async def test_delete_answer_endpoint(override_get_db, test_client: AsyncClient):
    # 1. Сначала создаём вопрос, чтобы было к чему привязывать ответ
    question_payload = {"text": "Вопрос, к которому будет ответ"}
    q_resp = await test_client.post("/api/questions/", json=question_payload)
    assert q_resp.status_code == 201

    created_question = q_resp.json()
    question_id = created_question["id"]

    # 2. Создаём ответ к этому вопросу
    answer_payload = {
        "text": "Какой-то ответ",
        "user_id": "user_1",
    }

    a_resp = await test_client.post(f"/api/answers/{question_id}", json=answer_payload)
    assert a_resp.status_code == 201

    created_answer = a_resp.json()
    answer_id = created_answer["id"]

    # 3. Удаляем существующий ответ
    delete_resp = await test_client.delete(f"/api/answers/{answer_id}")
    assert delete_resp.status_code == 204
    # Обычно при 204 тело пустое
    assert delete_resp.content in (b"", None)

    # 4. Проверяем, что ответ действительно удалён:
    #    запрос на него должен вернуть 404
    get_resp = await test_client.get(f"/api/answers/{answer_id}")
    assert get_resp.status_code == 404

    # 5. Повторная попытка удалить тот же ответ — тоже 404
    delete_again_resp = await test_client.delete(f"/api/answers/{answer_id}")
    assert delete_again_resp.status_code == 404

    error_data = delete_again_resp.json()
    assert error_data["detail"] == f"Answer with id {answer_id} not found."

