from ..routers.todos import get_db, get_current_user
from fastapi import status
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_authenticated(test_todo):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    # test_todo 값 사용
    assert response.json() == [
        {"id": test_todo.id, "title": test_todo.title, "description": test_todo.description,
         "priority": test_todo.priority, "complete": test_todo.complete, "owner_id": test_todo.owner_id,
         "category_id": test_todo.category_id}
    ]


def test_read_all_authenticated_with_complete(test_todos):
    response = client.get("/?complete=True")
    expected = [
        {
            "id": todo.id,
            "title": todo.title,
            "description": todo.description,
            "priority": todo.priority,
            "complete": todo.complete,
            "owner_id": todo.owner_id,
            "category_id": todo.category_id
        }
        for todo in test_todos if todo.complete is True
    ]
    assert response.status_code == status.HTTP_200_OK

    assert response.json() == expected

    response = client.get("/?complete=False")
    expected = [
        {
            "id": todo.id,
            "title": todo.title,
            "description": todo.description,
            "priority": todo.priority,
            "complete": todo.complete,
            "owner_id": todo.owner_id,
            "category_id": todo.category_id
        }
        for todo in test_todos if todo.complete is False
    ]

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected


def test_read_one_authenticated(test_todo):
    response = client.get("/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"id": test_todo.id, "title": test_todo.title, "description": test_todo.description,
                               "priority": test_todo.priority, "complete": test_todo.complete,
                               "owner_id": test_todo.owner_id,
                               "category_id": test_todo.category_id}


def test_read_one_authenticated_not_found(test_todo):
    response = client.get("/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}


def test_create_todo(test_todo):
    request_data = {
        "title": "New Todo",
        "description": "New Description",
        "priority": 3,
        "complete": False,
        "category_id": 1
    }

    response = client.post("/todo", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == request_data.get("title")
    assert model.description == request_data.get("description")
    assert model.priority == request_data.get("priority")
    assert model.complete == request_data.get("complete")


def test_update_todo(test_todo):
    request_data = {
        "title": "Updated Todo",
        "description": "Updated Description",
        "priority": 1,
        "complete": True,
    }

    response = client.put("/todo/1", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == request_data.get("title")
    assert model.description == request_data.get("description")
    assert model.priority == request_data.get("priority")
    assert model.complete == request_data.get("complete")


def test_update_todo_not_found(test_todo):
    request_data = {
        "title": "Updated Todo",
        "description": "Updated Description",
        "priority": 1,
        "complete": True,
    }

    response = client.put("/todo/999", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}


def test_delete_todo(test_todo):
    response = client.delete("/todo/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_delete_todo_not_fount(test_todo):
    response = client.delete("/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}
