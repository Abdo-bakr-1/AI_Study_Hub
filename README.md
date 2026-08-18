# AI Study Hub

A study-management web application built with **Django (MVT)** and **PostgreSQL**. It helps a registered user organise tasks, notes, and learning resources from a single dashboard, track study activity with charts, and chat with a built-in **AI Study Assistant** — all without Django REST Framework or any frontend framework.

> Built as a Django Web Development training project. Backend: Python + Django. Frontend: Django Templates + HTML/CSS/vanilla JavaScript.

---

## Features

**Authentication**
- Register, login, logout
- Profile page with image upload + update profile info
- Change password
- Email verification (token based)
- Password reset (token based)

**Dashboard**
- Statistics cards: total / completed / pending tasks, total notes, total resources
- Recent activity feed (from an activity log)
- Quick actions (add task / note / resource, open AI assistant)
- Charts (Chart.js): completed vs pending, tasks by priority, notes by category — all from the logged-in user's data

**Study Planner (Tasks)**
- Full CRUD + mark complete/uncomplete
- Title, description, due date, priority (Low/Medium/High), status, categories (M2M)
- Filtering by status, priority, category + pagination

**Notes**
- Full CRUD, categories (M2M)
- JavaScript **live search** across title + content
- Filter by category, pagination
- **PDF export** of the user's notes

**Learning Resources**
- Full CRUD, resource type (Article/Video/Documentation/Course/Book/Other), categories (M2M)
- Safe external link handling, filtering, pagination

**AI Chat Assistant** (`/ai-chat/`)
- Modern chat UI: history, user/AI bubbles, input, send, loading + error states
- Multiple conversations, per-user isolation, clear + new conversation
- Isolated **service layer** (`ai_assistant/services.py`) — OpenAI-compatible; graceful offline fallback when no API key is set
- Optional user study-data context (e.g. "what tasks are due this week?")

**Other**
- Dark mode toggle (persisted in `localStorage`)
- Responsive custom CSS (desktop → mobile)
- Django admin for all models
- Friendly 403 / 404 / 500 pages
- Security: CSRF, auth checks, per-user queryset ownership, secrets via env vars

---

## Technologies

- **Python** 3.12
- **Django** 5.1 (MVT, Django Templates, no DRF)
- **PostgreSQL**
- **HTML / CSS / vanilla JavaScript** (Chart.js via CDN for charts)
- **reportlab** for PDF export
- **Pillow** for image uploads
- **requests** for the AI provider HTTP client
- **django-environ** for environment variables
- AI provider: any **OpenAI-compatible** Chat Completions API (OpenAI, Groq, OpenRouter, local, …)

---

## Project Structure

```
Project/
├── manage.py
├── requirements.txt
├── .env.example          # copy to .env
├── .gitignore
├── config/               # project settings, root urls, wsgi/asgi
├── core/                 # landing page, ActivityLog model, context processor, template tags
├── accounts/             # Profile, EmailVerification, PasswordResetToken, auth views
├── dashboard/            # dashboard view (stats, charts, activity)
├── planner/              # Task + TaskCategory (tasks CRUD)
├── notes/                # Note + NoteCategory (notes CRUD, live search, PDF export)
├── resources/            # Resource + ResourceCategory (resources CRUD)
├── ai_assistant/         # Conversation + Message, AI service layer, chat views
├── templates/            # base.html, registration/, includes/, per-app templates, error pages
├── static/               # css/styles.css, js/(main|charts|chat|notes-search).js
├── media/                # uploaded profile images (git-ignored)
└── docs/                 # ERD image + database backup
```

Each app keeps a clean split of `models.py`, `forms.py`, `views.py`, `urls.py`, `admin.py`. AI provider logic lives only in `ai_assistant/services.py`.

---

## Installation

### 1. Clone and create a virtual environment

```bash
git clone <your-repo-url>
cd Project

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env              # Windows: copy .env.example .env
```

Then edit `.env` (see **Environment Variables** below).

---

## Database Setup (PostgreSQL)

1. Install PostgreSQL and make sure the server is running.
2. Create the database and (optionally) a user:

```bash
# Using the default postgres superuser:
psql -U postgres -c "CREATE DATABASE ai_study_hub;"

# Or create a dedicated user:
psql -U postgres -c "CREATE USER studyhub WITH PASSWORD 'your_db_password';"
psql -U postgres -c "CREATE DATABASE ai_study_hub OWNER studyhub;"
```

3. Put the matching credentials in `.env` (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`).

> A quick SQLite fallback exists for trials only — set `USE_SQLITE=True`. PostgreSQL is the intended final database.

---

## Environment Variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key. Generate a fresh one for production. |
| `DEBUG` | `True` in development, `False` in production. |
| `ALLOWED_HOSTS` | Comma-separated hostnames. |
| `USE_SQLITE` | `True` to use SQLite instead of PostgreSQL (trial only). |
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` | PostgreSQL connection. |
| `EMAIL_BACKEND` | Console backend by default (prints emails to terminal). Use SMTP for real email. |
| `EMAIL_HOST` / `EMAIL_PORT` / `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` / `EMAIL_USE_TLS` | SMTP settings. |
| `DEFAULT_FROM_EMAIL` | From address for verification / reset emails. |
| `AI_API_KEY` | API key for the AI provider. **Leave blank to use the offline fallback assistant.** |
| `AI_API_BASE_URL` | Base URL of an OpenAI-compatible API (default Gemini `https://generativelanguage.googleapis.com/v1beta/openai`). |
| `AI_MODEL` | Model name (e.g. `gemini-3.6-flash`). |
| `AI_REQUEST_TIMEOUT` | Request timeout in seconds (default 60 for Gemini). |
| `AI_MAX_TOKENS` | Max tokens for the AI response. |

Secrets are **never** hard-coded — everything sensitive is read from `.env`, which is git-ignored.

---

## AI Setup

The assistant talks to any **OpenAI-compatible Chat Completions** endpoint through the service layer in `ai_assistant/services.py`.

1. Get an API key from your provider (e.g. Google Gemini, OpenAI, Groq, OpenRouter).
2. Set in `.env`:
   ```env
   AI_API_KEY=your_key_here
   AI_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
   AI_MODEL=gemini-3.6-flash
   AI_REQUEST_TIMEOUT=60
   ```
3. Restart the server.

If `AI_API_KEY` is empty (or the provider call fails), the app automatically uses a built-in **offline fallback** assistant so the chat feature still works during development and grading. This is intentional and documented, and no secrets are ever exposed to the browser.

---

## Running the Project

```bash
source venv/bin/activate          # Windows: venv\Scripts\activate

python manage.py makemigrations
python manage.py migrate

python manage.py createsuperuser

python manage.py collectstatic    # for production static serving
python manage.py runserver
```

Open http://127.0.0.1:8000/

- App: `/` → register/login → `/dashboard/`
- Admin: `/admin/`
- AI chat: `/ai-chat/`

Email verification and password-reset links are printed to the terminal when using the console email backend.

---

## ERD

The full entity–relationship diagram is in [`docs/erd.png`](docs/erd.png).

Main relationships:

```
User 1 ── 1 Profile
User 1 ── N Task / Note / Resource / Conversation / ActivityLog
User 1 ── N EmailVerification / PasswordResetToken
Category (per type) N ── N Task / Note / Resource     (Many-to-Many)
Conversation 1 ── N Message
```

- One-to-One: 1 (User ↔ Profile)
- One-to-Many: User→Tasks/Notes/Resources/Conversations/ActivityLogs, Conversation→Messages, …
- Many-to-Many: Task↔TaskCategory, Note↔NoteCategory, Resource↔ResourceCategory

---

## Database Backup

A PostgreSQL backup can be produced and restored with `pg_dump` / `psql`:

```bash
# Create a backup (plain SQL)
pg_dump -U postgres -d ai_study_hub -f docs/ai_study_hub_backup.sql

# Restore into a fresh database
psql -U postgres -c "CREATE DATABASE ai_study_hub;"
psql -U postgres -d ai_study_hub -f docs/ai_study_hub_backup.sql
```

The provided backup in `docs/` was generated with the command above.

---

## Screenshots

Add screenshots to a `docs/screenshots/` folder and reference them here:

- Login / Register
- Dashboard (light + dark)
- Task list / Task form
- Notes (with live search) / Resources
- Profile
- AI Chat
- Mobile / responsive view

---

## Security Notes

- All list/detail/edit/delete views filter by the logged-in user — a user can never access another user's tasks, notes, resources, conversations, or messages.
- CSRF protection is enabled on all forms and the AJAX chat request.
- Passwords use Django's hashing + validators.
- Uploaded profile images are validated (type/size) and a default avatar is shown when none exists.
- API keys and other secrets live only in `.env` (git-ignored); a `.env.example` documents them.

---

## Team

| Name | Role |
|---|---|
| _Team member 1_ | _placeholder_ |
| _Team member 2_ | _placeholder_ |
