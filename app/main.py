import secrets
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app import config
from app.db import Base, engine, get_session
from app.models import Book, Loan, Member
from app.repositories import BookRepository, LoanRepository
from app.services.books import add_book_by_isbn
from app.services.loans import can_borrow

LIBRARIAN_ID = 1
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
SessionDep = Annotated[Session, Depends(get_session)]


def init_db(bind=engine) -> None:
    Base.metadata.create_all(bind)
    with Session(bind) as session:
        if session.get(Member, LIBRARIAN_ID) is None:
            session.add(Member(id=LIBRARIAN_ID, name="Bibliothécaire", age=30))
            session.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Biblio", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=config.SECRET_KEY)


# ---------- API ----------


def require_token(creds: Annotated[HTTPAuthorizationCredentials | None, Depends(HTTPBearer(auto_error=False))]) -> None:
    if creds is None or not secrets.compare_digest(creds.credentials, config.API_TOKEN):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentification requise")


class BookIn(BaseModel):
    isbn: str = Field(min_length=10, max_length=13)
    title: str = Field(min_length=1)
    author: str | None = None
    year: int | None = None


class BookOut(BookIn):
    id: int


class LoanIn(BaseModel):
    book_id: int
    member_id: int


class LoanOut(LoanIn):
    id: int


@app.get("/health")
def health(session: SessionDep):
    try:
        session.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse({"status": "database unavailable"}, status.HTTP_503_SERVICE_UNAVAILABLE)
    return {"status": "ok"}


@app.get("/books", response_model=list[BookOut], dependencies=[Depends(require_token)])
def list_books(session: SessionDep):
    return BookRepository(session).list_all()


@app.post("/books", response_model=BookOut, status_code=201, dependencies=[Depends(require_token)])
def create_book(book: BookIn, session: SessionDep):
    try:
        return BookRepository(session).add(Book(**book.model_dump()))
    except IntegrityError:
        raise HTTPException(status.HTTP_409_CONFLICT, "ISBN déjà enregistré") from None


@app.post("/books/import/{isbn}", response_model=BookOut, status_code=201, dependencies=[Depends(require_token)])
def import_book(isbn: str, session: SessionDep):
    return BookRepository(session).add(add_book_by_isbn(isbn))


@app.post("/loans", response_model=LoanOut, status_code=201, dependencies=[Depends(require_token)])
def create_loan(loan: LoanIn, session: SessionDep):
    return borrow(session, loan.book_id, loan.member_id)


def borrow(session: Session, book_id: int, member_id: int) -> Loan:
    member = session.get(Member, member_id)
    if member is None or session.get(Book, book_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Livre ou adhérent inconnu")
    loans = LoanRepository(session)
    if loans.is_borrowed(book_id):
        raise HTTPException(status.HTTP_409_CONFLICT, "Livre déjà emprunté")
    if not can_borrow(member_id, member.age, loans.count_active(member_id)):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Nombre maximal d'emprunts atteint")
    return loans.add(Loan(book_id=book_id, member_id=member_id))


# ---------- Pages ----------


def logged_in(request: Request) -> bool:
    return request.session.get("user") == config.ADMIN_EMAIL


def page(request: Request, name: str, **context):
    if not logged_in(request):
        return RedirectResponse("/login", status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(request, name, context)


@app.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse(request, "login.html", {"error": None})


@app.post("/login")
def login(request: Request, email: Annotated[str, Form()], password: Annotated[str, Form()]):
    if email == config.ADMIN_EMAIL and secrets.compare_digest(password, config.ADMIN_PASSWORD):
        request.session["user"] = email
        return RedirectResponse("/", status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(request, "login.html", {"error": "Identifiants incorrects"}, status_code=401)


@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status.HTTP_303_SEE_OTHER)


@app.get("/")
def catalog(request: Request, session: SessionDep):
    loans = LoanRepository(session)
    books = [(b, loans.is_borrowed(b.id)) for b in BookRepository(session).list_all()]
    return page(request, "catalog.html", books=books)


@app.get("/books/new")
def book_form(request: Request):
    return page(request, "book_form.html", error=None)


@app.post("/books/new")
def book_submit(
    request: Request,
    session: SessionDep,
    isbn: Annotated[str, Form()],
    title: Annotated[str, Form()],
    author: Annotated[str, Form()] = "",
):
    if not logged_in(request):
        return RedirectResponse("/login", status.HTTP_303_SEE_OTHER)
    try:
        BookRepository(session).add(Book(isbn=isbn.strip(), title=title.strip(), author=author.strip() or None))
    except IntegrityError:
        session.rollback()
        return page(request, "book_form.html", error="Cet ISBN existe déjà")
    return RedirectResponse("/", status.HTTP_303_SEE_OTHER)


@app.post("/books/{book_id}/borrow")
def borrow_submit(request: Request, session: SessionDep, book_id: int):
    if not logged_in(request):
        return RedirectResponse("/login", status.HTTP_303_SEE_OTHER)
    borrow(session, book_id, LIBRARIAN_ID)
    return RedirectResponse("/loans", status.HTTP_303_SEE_OTHER)


@app.get("/loans")
def my_loans(request: Request, session: SessionDep):
    loans = session.scalars(select(Loan).where(Loan.member_id == LIBRARIAN_ID)).all()
    return page(request, "loans.html", loans=loans)
