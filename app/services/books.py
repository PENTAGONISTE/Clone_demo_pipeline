import httpx

from app import config
from app.models import Book


def fetch_title(isbn: str) -> str:
    response = httpx.get(f"{config.ISBN_SERVICE_URL}/{isbn}", timeout=5)
    response.raise_for_status()
    return response.json()["title"]


def add_book_by_isbn(isbn: str) -> Book:
    return Book(isbn=isbn, title=fetch_title(isbn))
