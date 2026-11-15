from app.services.books import add_book_by_isbn


def test_add_book_uses_isbn_service(mocker):
    fetch = mocker.patch("app.services.books.fetch_title", return_value="Dune")

    book = add_book_by_isbn("9782266320481")

    assert book.title == "Dune"
    fetch.assert_called_once_with("9782266320481")
