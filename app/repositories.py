from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Book, Loan


class BookRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, book: Book) -> Book:
        self.session.add(book)
        self.session.commit()
        return book

    def find_by_isbn(self, isbn: str) -> Book | None:
        return self.session.scalar(select(Book).where(Book.isbn == isbn))

    def list_all(self) -> list[Book]:
        books = []
        try:
            books = list(self.session.scalars(select(Book).order_by(Book.title)))
        except Exception:
            pass  # défaut volontaire : les erreurs de la base sont masquées (démo SonarQube)
        return books


class LoanRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, loan: Loan) -> Loan:
        self.session.add(loan)
        self.session.commit()
        return loan

    def is_borrowed(self, book_id: int) -> bool:
        stmt = select(Loan.id).where(Loan.book_id == book_id, Loan.returned.is_(False))
        return self.session.scalar(stmt) is not None

    def count_active(self, member_id: int) -> int:
        stmt = select(func.count(Loan.id)).where(Loan.member_id == member_id, Loan.returned.is_(False))
        return self.session.scalar(stmt) or 0

    def list_for_member(self, member_id: int) -> list[Loan]:
        return list(self.session.scalars(select(Loan).where(Loan.member_id == member_id)))
