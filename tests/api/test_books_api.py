def test_create_book_returns_201(client, auth):
    r = client.post("/books", headers=auth, json={"isbn": "9782266320481", "title": "Dune"})
    assert r.status_code == 201
    assert r.json()["title"] == "Dune"


def test_book_without_title_is_rejected(client, auth):
    r = client.post("/books", headers=auth, json={"isbn": "9782266320481"})
    assert r.status_code == 422


def test_duplicate_isbn_returns_409(client, auth):
    book = {"isbn": "9782266320481", "title": "Dune"}
    client.post("/books", headers=auth, json=book)
    assert client.post("/books", headers=auth, json=book).status_code == 409


def test_books_require_authentication(client):
    assert client.get("/books").status_code == 401


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}
