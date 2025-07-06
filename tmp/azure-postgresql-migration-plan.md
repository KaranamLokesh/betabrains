# Azure App Service + PostgreSQL Migration Plan

## 1. Overview of Current State
- App uses SQLite by default, with optional PostgreSQL via `DATABASE_URL`.
- No Azure-specific deployment instructions or WSGI entrypoint.
- No production WSGI server in requirements.

## 2. Overview of Final State
- App can be deployed to Azure App Service using PostgreSQL as the backend.
- Azure deployment instructions are present in the README.
- WSGI entrypoint (`app/wsgi.py`) is available for production.
- `gunicorn` is included in requirements for production serving.

## 3. Files to Change
- `README.md`: Add Azure deployment and PostgreSQL setup instructions.
- `requirements.txt`: Add `gunicorn` for production.
- `app/wsgi.py`: Add WSGI entrypoint for Azure.

## 4. Checklist
- [x] Add `app/wsgi.py` for WSGI entrypoint
- [x] Add `gunicorn` to `requirements.txt`
- [x] Update `README.md` with Azure and PostgreSQL deployment steps

## Additional Ideas (Not Implemented)
- Add `.env.example` for Azure
- Automate Azure deployment with GitHub Actions
- Add troubleshooting for common Azure issues 