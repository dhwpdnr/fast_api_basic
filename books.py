from fastapi import FastAPI, Body

app = FastAPI()

BOOKS = [
    {"title": "Harry Potter", "author": "J.K. Rowling", "category": "Fantasy"},
    {"title": "The Lord of the Rings", "author": "J.R.R. Tolkien", "category": "Fantasy"},
    {"title": "The Da Vinci Code", "author": "Dan Brown", "category": "Thriller"},
    {"title": "The Alchemist", "author": "Paulo Coelho", "category": "Fantasy"},
    {"title": "The Catcher in the Rye", "author": "J.D. Salinger", "category": "Fiction"},
    {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "category": "Fiction"},
]


@app.get("/books")
async def read_all_books():
    return BOOKS


@app.get("/books/mybook")
async def read_all_books():
    return {"book_title": "My Favorite Book"}


# path parameter
@app.get("/books/{book_title}")
async def read_book(book_title: str):
    for book in BOOKS:
        if book.get("title").casefold() == book_title.casefold():
            return book
    return {"error": "Book not found"}


# query parameter
@app.get("/books/")
async def read_category_by_query(category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get("category").casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return


# multiple parameters
@app.get("/books/{book_author}/")
async def read_author_by_category(book_author: str, category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get("author").casefold() == book_author.casefold() and book.get(
                "category").casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return


@app.post("/books/create_book")
async def create_book(new_book=Body()):
    BOOKS.append(new_book)


@app.put("/books/update_book")
async def update_book(updated_book=Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get("title").casefold() == updated_book.get("title").casefold():
            BOOKS[i] = updated_book
            return {"message": "Book updated successfully"}


@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title: str):
    for i in range(len(BOOKS)):
        if BOOKS[i].get("title").casefold() == book_title.casefold():
            BOOKS.pop(i)
            return {"message": "Book deleted successfully"}
    return {"error": "Book not found"}
