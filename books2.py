from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int

    def __init__(self, id, title, author, description, rating):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating


class BookRequest(BaseModel):
    id: Optional[int] = Field(default=None, description="id is not needed")
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(max_length=100)
    rating: int = Field(gt=0, le=5)

    model_config = {
        "json_schema_extra": {
            "example": [
                {
                    "title": "The name of the book",
                    "author": "The full name of the author",
                    "description": "A brief summary of the book",
                    "category": "The category of the book E.g. novel",
                }
            ]
        }
    }


BOOKS = [
    Book(1, "Computer Science", "John Doe", "A book about computer science", 5),
    Book(2, "Cooking", "Mary Smith", "A book about cooking", 4),
    Book(3, "Data Science", "Jane Doe", "A book about data science", 3),
    Book(4, "Python", "John Doe", "A book about Python programming", 1),
    Book(5, "Algorithms", "Jane Doe", "A book about algorithms", 2),
    Book(6, "Django", "author 1", "A book about Django", 5),
]


@app.get("/books")
async def read_all_books():
    return BOOKS


@app.post("/create_book")
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.dict())
    BOOKS.append(find_book_id(new_book))


def find_book_id(book: Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book
