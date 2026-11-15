import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./biblio.db")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret")
API_TOKEN = os.getenv("API_TOKEN", "dev-token")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "biblio@ensam.ma")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "secret")
ISBN_SERVICE_URL = os.getenv("ISBN_SERVICE_URL", "https://isbn.example.com/books")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "")
