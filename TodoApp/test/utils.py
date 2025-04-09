from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from ..database import Base
from fastapi.testclient import TestClient
import pytest
from ..main import app
from ..models import Todos, Users, Category
from ..routers.auth import bcrypt_context

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {"username": "testuser", "id": 1, "user_role": "admin"}


client = TestClient(app)


@pytest.fixture
def test_category():
    category = Category(name="Test Category")

    db = TestingSessionLocal()
    db.add(category)
    db.commit()
    db.refresh(category)
    yield category
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM categories;"))
        connection.commit()


@pytest.fixture
def test_todo(test_category):
    todo = Todos(
        title="Learn to code",
        description="Test Description",
        priority=5,
        complete=False,
        owner_id=1,
        category_id=test_category.id,
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()


@pytest.fixture
def test_todos(test_category):
    todo1 = Todos(
        title="Learn to code",
        description="Test Description",
        priority=5,
        complete=False,
        owner_id=1,
        category_id=test_category.id,
    )
    todo2 = Todos(
        title="Learn to code",
        description="Test Description",
        priority=5,
        complete=True,
        owner_id=1,
        category_id=test_category.id,
    )

    db = TestingSessionLocal()
    db.add(todo1)
    db.add(todo2)
    db.commit()
    yield [todo1, todo2]
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()


@pytest.fixture
def test_user():
    user = Users(
        username="testuser",
        email="test@email.com",
        first_name="Test",
        last_name="User",
        hashed_password=bcrypt_context.hash("password"),
        role="admin",
        phone_number="1234567890",
    )

    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()
