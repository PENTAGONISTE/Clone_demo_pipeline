import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Book
from app.repositories import BookRepository

pytestmark = pytest.mark.integration


def test_save_and_find_book(session):
    repo = BookRepository(session)
    repo.add(Book(isbn="9782266320481", title="Dune"))

    assert repo.find_by_isbn("9782266320481").title == "Dune"


def test_isbn_is_unique(session):
    repo = BookRepository(session)
    repo.add(Book(isbn="9782266320481", title="Dune"))

    with pytest.raises(IntegrityError):
        repo.add(Book(isbn="9782266320481", title="Dune, édition poche"))
