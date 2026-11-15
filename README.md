# Biblio

Application de démonstration du module DevOps (séance 6) : gestion des livres et des emprunts d'une médiathèque.
FastAPI, SQLAlchemy, PostgreSQL et pages Jinja2.

## Démarrer

```bash
python3.12 -m venv .venv && source .venv/bin/activate
make install        # dépendances + navigateur Chromium pour Playwright
make run            # http://localhost:8000, connexion : biblio@ensam.ma / secret
```

Avec PostgreSQL : `docker compose up --build`.

## Tests

| Commande | Niveau | Prérequis |
| --- | --- | --- |
| `make lint` | Ruff | aucun |
| `make test` | unit + API | aucun |
| `make coverage` | unit + API, avec `coverage.xml` et `report.xml` | aucun |
| `make integration` | integration | Docker (Testcontainers) |
| `make e2e` | end-to-end | Chromium (`make install`) |

## Arborescence

```
app/          main.py (API + pages), models.py, repositories.py, services/, templates/
tests/        unit/  integration/  api/  e2e/
infra/        terraform/ (Hetzner Cloud)  ansible/ (déploiement)
sonar/        compose.yaml du serveur SonarQube
.gitlab-ci.yml  Dockerfile  compose.yaml  sonar-project.properties  Makefile
```

## API

Authentification : `Authorization: Bearer $API_TOKEN` (`dev-token` en local).

| Méthode | Endpoint | Réponse |
| --- | --- | --- |
| GET | `/health` | 200, ou 503 si la base est injoignable |
| GET | `/books` | liste des livres |
| POST | `/books` | 201, 409 si l'ISBN existe, 422 si un champ manque |
| POST | `/books/import/{isbn}` | 201, titre récupéré auprès du service ISBN |
| POST | `/loans` | 201, 403 au-delà du quota, 404, 409 si le livre est emprunté |

## Variables CI/CD du projet GitLab

`SONAR_HOST_URL`, `SONAR_TOKEN`, `HCLOUD_TOKEN`, `SSH_PUBLIC_KEY`, `SSH_PRIVATE_KEY`, `DB_PASSWORD`,
`SECRET_KEY`, `API_TOKEN`, `ADMIN_PASSWORD` : masquées et protégées.

## Défauts volontaires (support des exercices)

- `app/services/fees.py` : le plafond de pénalité n'est pas appliqué (bug à révéler par un test).
- `app/repositories.py` : `list_all` masque les erreurs de la base (problème signalé par SonarQube).
- `infra/terraform/firewall.tf` : SSH ouvert à `0.0.0.0/0` (règle signalée par Checkov).
- Couverture initiale d'environ 60 %, sous le seuil de 80 % visé dans les exercices.
