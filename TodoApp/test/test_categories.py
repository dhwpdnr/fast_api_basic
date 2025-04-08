from ..routers.categories import get_db
from fastapi import status
from .utils import *

app.dependency_overrides[get_db] = override_get_db


def test_read_all_category(test_category):
    response = client.get("/categories/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {"id": test_category.id, "name": test_category.name}
    ]


def test_create_category(test_category):
    request_data = {
        "name": "New Category"
    }

    response = client.post("/categories/", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model = db.query(Category).filter(Category.name == request_data["name"]).first()
    assert model is not None
    assert model.name == request_data["name"]


def test_create_category_already_exists(test_category):
    request_data = {
        "name": test_category.name
    }

    response = client.post("/categories/", json=request_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Category already exists"}


def test_read_one_category(test_category):
    response = client.get(f"/categories/{test_category.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"id": test_category.id, "name": test_category.name}


def test_read_one_category_not_found():
    response = client.get("/categories/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Category not found"}


def test_delete_category(test_category):
    response = client.delete(f"/categories/{test_category.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Category).filter(Category.id == test_category.id).first()
    assert model is None


def test_delete_category_not_found(test_category):
    response = client.delete("/categories/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Category not found"}
