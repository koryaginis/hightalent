import pytest
from httpx import AsyncClient
from dateutil.parser import isoparse

@pytest.mark.asyncio
async def test_create_question_endpoint(override_get_db, test_client: AsyncClient):
    """
    Тест для эндпоинта создания вопроса.
    """
    payload = {"text": "Какой сегодня день?"}

    response = await test_client.post("/api/questions/", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["text"] == payload["text"]
    assert data["answers"] == []
    assert "created_at" in data
    assert isinstance(data["id"], int)

    isoparse(data["created_at"])

@pytest.mark.asyncio
async def test_get_questions_list_endpoint(override_get_db, test_client: AsyncClient):
    """
    Тест для эндпоинта получения всех вопросов.
    """
    payload1 = {"text": "Первый вопрос?"}
    payload2 = {"text": "Второй вопрос?"}

    resp1 = await test_client.post("/api/questions/", json=payload1)
    resp2 = await test_client.post("/api/questions/", json=payload2)

    assert resp1.status_code == 201
    assert resp2.status_code == 201

    response = await test_client.get("/api/questions/")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 2

    first_question = data[0]
    assert "id" in first_question
    assert "text" in first_question
    assert "created_at" in first_question
    assert "answers" in first_question

    assert first_question["text"] in {payload1["text"], payload2["text"]}
    assert isinstance(first_question["answers"], list)

    from dateutil.parser import isoparse
    isoparse(first_question["created_at"])

@pytest.mark.asyncio
async def test_get_answers_by_question_id(override_get_db, test_client: AsyncClient):
    """
    Тест для эндпоинта получения вопроса и ответов на него.
    """
    question_payload = {"text": "Какой сегодня день?"}
    q_resp = await test_client.post("/api/questions/", json=question_payload)
    assert q_resp.status_code == 201
    created_question = q_resp.json()
    question_id = created_question["id"]

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

    resp_ok = await test_client.get(f"/api/questions/{question_id}")
    assert resp_ok.status_code == 200

    data = resp_ok.json()

    assert data["id"] == question_id
    assert data["text"] == question_payload["text"]
    isoparse(data["created_at"])

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

    non_existing_id = question_id + 1000
    resp_not_found = await test_client.get(f"/api/questions/{non_existing_id}")
    assert resp_not_found.status_code == 404
    detail = resp_not_found.json()["detail"]
    assert detail == f"Question with id {non_existing_id} not found."

@pytest.mark.asyncio
async def test_delete_question_endpoint(override_get_db, test_client: AsyncClient):
    """
    Тест для эндпоинта удаления вопроса.
    """
    question_payload = {"text": "Вопрос для удаления"}
    create_resp = await test_client.post("/api/questions/", json=question_payload)
    assert create_resp.status_code == 201

    created_question = create_resp.json()
    question_id = created_question["id"]

    delete_resp = await test_client.delete(f"/api/questions/{question_id}")
    assert delete_resp.status_code == 204
    assert delete_resp.content in (b"", None)

    get_resp = await test_client.get(f"/api/questions/{question_id}")
    assert get_resp.status_code == 404

    delete_again_resp = await test_client.delete(f"/api/questions/{question_id}")
    assert delete_again_resp.status_code == 404
    data = delete_again_resp.json()
    assert data["detail"] == f"Question with id {question_id} not found."

