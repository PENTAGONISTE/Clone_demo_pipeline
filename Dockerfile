# étape 1 : installer les dépendances
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# étape 2 : image livrée
FROM python:3.12-slim
RUN useradd --create-home biblio
COPY --from=builder /install /usr/local
COPY app/ /app/app/
WORKDIR /app
USER biblio
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
