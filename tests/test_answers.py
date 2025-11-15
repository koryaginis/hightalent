import pytest
from httpx import AsyncClient
from dateutil.parser import isoparse

@pytest.mark.asyncio
async def test_create_answer_endpoint(override_get_db, test_client: AsyncClient):
    """
    Тест для эндпоинта создания ответа на вопрос.
    """
    question_payload = {"text": "Какой сегодня день?"}
    q_resp = await test_client.post("/api/questions/", json=question_payload)
    assert q_resp.status_code == 201

    created_question = q_resp.json()
    question_id = created_question["id"]

    answer_payload = {
        "text": "Сегодня хороший день",
        "user_id": "user_1",
    }

    a_resp = await test_client.post(f"/api/answers/{question_id}", json=answer_payload)
    assert a_resp.status_code == 201

    data = a_resp.json()

    assert "id" in data
    assert data["question_id"] == question_id
    assert data["text"] == answer_payload["text"]
    assert data["user_id"] == answer_payload["user_id"]
    assert "created_at" in data
    isoparse(data["created_at"])

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
    """
    Тест для эндпоинта получения ответа по id.
    """
    question_payload = {"text": "Какой сегодня день?"}
    q_resp = await test_client.post("/api/questions/", json=question_payload)
    assert q_resp.status_code == 201

    created_question = q_resp.json()
    question_id = created_question["id"]

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

    get_resp = await test_client.get(f"/api/answers/{answer_id}")
    assert get_resp.status_code == 200

    data = get_resp.json()

    assert data["id"] == answer_id
    assert data["question_id"] == question_id
    assert data["text"] == answer_payload["text"]
    assert data["user_id"] == answer_payload["user_id"]
    assert "created_at" in data
    isoparse(data["created_at"])

    non_existing_id = answer_id + 1000

    not_found_resp = await test_client.get(f"/api/answers/{non_existing_id}")
    assert not_found_resp.status_code == 404

    error_data = not_found_resp.json()
    assert error_data["detail"] == f"Answer with id {non_existing_id} not found."

@pytest.mark.asyncio
async def test_delete_answer_endpoint(override_get_db, test_client: AsyncClient):
    """
    Тест для эндпоинта удаления ответа на вопрос.
    """
    question_payload = {"text": "Вопрос, к которому будет ответ"}
    q_resp = await test_client.post("/api/questions/", json=question_payload)
    assert q_resp.status_code == 201

    created_question = q_resp.json()
    question_id = created_question["id"]

    answer_payload = {
        "text": "Какой-то ответ",
        "user_id": "user_1",
    }

    a_resp = await test_client.post(f"/api/answers/{question_id}", json=answer_payload)
    assert a_resp.status_code == 201

    created_answer = a_resp.json()
    answer_id = created_answer["id"]

    delete_resp = await test_client.delete(f"/api/answers/{answer_id}")
    assert delete_resp.status_code == 204
    assert delete_resp.content in (b"", None)

    get_resp = await test_client.get(f"/api/answers/{answer_id}")
    assert get_resp.status_code == 404

    delete_again_resp = await test_client.delete(f"/api/answers/{answer_id}")
    assert delete_again_resp.status_code == 404

    error_data = delete_again_resp.json()
    assert error_data["detail"] == f"Answer with id {answer_id} not found."

