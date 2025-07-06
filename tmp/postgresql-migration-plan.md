# PostgreSQL Migration Feature Plan

## 1. Overview of Current State
- The application uses SQLite as the default database, configured via `config.py` using SQLAlchemy.
- The database URI is set to SQLite unless the `DATABASE_URL` environment variable is provided.
- No PostgreSQL driver is included in `requirements.txt`.
- The README only documents SQLite usage.

## 2. Overview of Final State
- The application supports PostgreSQL as the primary database when `DATABASE_URL` is set to a PostgreSQL URI.
- The `psycopg2-binary` driver is included in `requirements.txt`.
- The README provides clear instructions for using PostgreSQL, including how to set the `DATABASE_URL`.
- No code changes are required in the app logic due to SQLAlchemy's abstraction.

## 3. Files to Change
- `requirements.txt`: Add `psycopg2-binary` for PostgreSQL support.
- `README.md`: Add instructions for using PostgreSQL and setting the `DATABASE_URL` environment variable.

## 4. Checklist
- [x] Add `psycopg2-binary` to `requirements.txt`
- [x] Update `README.md` with PostgreSQL setup instructions
- [ ] (Optional) Test the app with a PostgreSQL database and update documentation if issues are found

## Additional Ideas (Not Implemented)
- Provide a sample `.env.example` file
- Add automated tests for both SQLite and PostgreSQL backends
- Document common PostgreSQL migration issues 