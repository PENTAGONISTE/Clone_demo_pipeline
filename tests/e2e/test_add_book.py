import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.e2e


def login(page: Page, base_url: str) -> None:
    page.goto(f"{base_url}/login")
    page.get_by_label("Adresse e-mail").fill("biblio@ensam.ma")
    page.get_by_label("Mot de passe").fill("secret")
    page.get_by_role("button", name="Se connecter").click()


def test_librarian_adds_a_book(page: Page, base_url):
    login(page, base_url)

    page.get_by_role("link", name="Ajouter un livre").click()
    page.get_by_label("ISBN").fill("9782266320481")
    page.get_by_label("Titre").fill("Dune")
    page.get_by_role("button", name="Enregistrer").click()

    expect(page.get_by_role("row", name="Dune")).to_be_visible()


def test_protected_page_redirects_to_login(page: Page, base_url):
    page.context.clear_cookies()
    page.goto(f"{base_url}/books/new")
    expect(page.get_by_role("heading", name="Connexion")).to_be_visible()
