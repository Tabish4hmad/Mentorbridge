# Mentorbridge

This is the V1 of the MentorBridge project.

Django backend scaffold with a starter API app.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
set POSTGRES_DB=mentor_project
set POSTGRES_USER=postgres
set POSTGRES_PASSWORD=your_postgres_password
python manage.py migrate
python manage.py runserver
```

## Endpoint

- `GET /api/health/` returns `{"status": "ok"}`
