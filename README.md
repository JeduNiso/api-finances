# Finances API

A RESTful backend API for personal finance management — built with **Django** + **Django REST Framework**. Handles family accounts, fixed/variable expenses, debts, and spending tracking with JWT authentication.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Framework | Django 5.0 + Django REST Framework 3.15 |
| Auth | JWT via `djangorestframework-simplejwt` |
| Database | MySQL (production) / SQLite (local dev) |
| MySQL driver | PyMySQL + cryptography (supports `caching_sha2_password`) |
| CORS | `django-cors-headers` |
| Server | Gunicorn |
| Deployment | Railway (Docker) |

---

## Project Structure

```
finances-django/
├── finances_api/          # Django project config
│   ├── settings.py        # Settings (auto-detects MySQL vs SQLite)
│   ├── urls.py            # Root URL conf + health check
│   └── wsgi.py
├── api/                   # Main application
│   ├── models.py          # All data models
│   ├── serializers.py     # DRF serializers
│   ├── views.py           # API views
│   ├── urls.py            # API routes
│   └── admin.py           # Django admin registration
├── Dockerfile
├── railway.toml
├── requirements.txt
└── .env.example
```

---

## Data Models

```
User ──┬── FamilyMember ──── Family
       ├── UserAccount  ──── Account ──── Bank
       ├── Spending
       └── Debt ──── DebtPayment

Account ──┬── Spending
          ├── Expense ──── ExpenseLog
          └── Debt
```

---

## API Endpoints

All protected routes require `Authorization: Bearer <token>`.

### Auth

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/auth/register` | Public | Register a new user |
| `POST` | `/api/auth/login` | Public | Login, returns access + refresh tokens |
| `POST` | `/api/auth/logout` | ✓ | Blacklist the refresh token |

### Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/dashboard` | Total balance, monthly spending, active debt summary |

### Families

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/families` | Create a family (current user becomes owner) |
| `GET` | `/api/families/mine` | Get the family the current user belongs to |
| `GET` | `/api/families/members` | List all members of the family |
| `POST` | `/api/families/invite` | Invite a user by email |
| `DELETE` | `/api/families/members/{user_id}` | Remove a member (owner only) |

### Accounts

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/accounts` | List accounts accessible by the current user |
| `POST` | `/api/accounts` | Create a new account |
| `PUT` | `/api/accounts/{id}` | Update an account |
| `DELETE` | `/api/accounts/{id}` | Delete an account |
| `GET` | `/api/accounts/{id}/summary` | Balance + monthly spending for an account |

### Spending *(gastos puntuales)*

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/spending/summary` | Total + breakdown by category (current month) |
| `GET` | `/api/spending` | List all spending entries |
| `POST` | `/api/spending` | Create a spending entry |
| `PUT` | `/api/spending/{id}` | Update a spending entry |
| `DELETE` | `/api/spending/{id}` | Delete a spending entry |

### Expenses *(gastos fijos)*

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/expenses/calendar` | Active expenses + payment log for current month |
| `GET` | `/api/expenses` | List all fixed expenses |
| `POST` | `/api/expenses` | Create a fixed expense |
| `PUT` | `/api/expenses/{id}` | Update a fixed expense |
| `DELETE` | `/api/expenses/{id}` | Delete a fixed expense |
| `POST` | `/api/expenses/{id}/pay` | Register a payment log entry |

### Debts

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/debts/summary` | Total active balance + count |
| `GET` | `/api/debts` | List all debts (includes payments + progress %) |
| `POST` | `/api/debts` | Create a debt |
| `PUT` | `/api/debts/{id}` | Update a debt |
| `DELETE` | `/api/debts/{id}` | Delete a debt |
| `POST` | `/api/debts/{id}/payment` | Register a payment, updates current balance |

### Catalogs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/banks` | List all banks |
| `GET` | `/api/categories` | List all categories |
| `POST` | `/api/categories` | Create a category |
| `PUT` | `/api/categories/{id}` | Update a category |
| `DELETE` | `/api/categories/{id}` | Delete a category |

### Users *(admin)*

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/users` | List all users |
| `POST` | `/api/users` | Create a user |
| `GET` | `/api/users/{id}` | Get a user |
| `PUT` | `/api/users/{id}` | Update a user |
| `DELETE` | `/api/users/{id}` | Delete a user |

---

## Auth Flow

```
POST /api/auth/register  →  { user, token, refresh }
POST /api/auth/login     →  { user, token, refresh }

# Use token on every protected request:
Authorization: Bearer <token>

# Logout – blacklists the refresh token
POST /api/auth/logout    →  { refresh: "<refresh_token>" }
```

---

## Local Development

### Prerequisites

- Python 3.12+

### Setup

```bash
# 1. Clone / enter the project
cd finances-django

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash)
# source .venv/bin/activate      # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations  (uses SQLite automatically when DB_HOST is not set)
python manage.py migrate

# 5. (Optional) Create a superuser for the admin panel
python manage.py createsuperuser

# 6. Start the development server
python manage.py runserver
```

The API is now available at `http://127.0.0.1:8000/api/`.

> **No `.env` needed for local dev.** When `DB_HOST` is not set, the app uses a local `db.sqlite3` file automatically.

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the values for production/staging:

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | insecure default |
| `DEBUG` | Enable debug mode | `False` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `*` |
| `DB_HOST` | MySQL host (leave empty to use SQLite) | *(empty)* |
| `DB_PORT` | MySQL port | `3306` |
| `DB_DATABASE` | Database name | `railway` |
| `DB_USERNAME` | Database user | `root` |
| `DB_PASSWORD` | Database password | *(empty)* |

---

## Deployment (Railway)

### Via Railway CLI

```bash
# Link to your Railway project
railway link

# Set environment variables
railway variables --set "SECRET_KEY=your-secret-key"
railway variables --set "DB_HOST=mysql.railway.internal"
railway variables --set "DB_PORT=3306"
railway variables --set "DB_DATABASE=railway"
railway variables --set "DB_USERNAME=root"
railway variables --set "DB_PASSWORD=your-db-password"
railway variables --set "DEBUG=False"

# Deploy
railway up
```

### What happens on deploy

1. Docker builds using `python:3.12-slim-bookworm`
2. Dependencies are installed via `pip`
3. `python manage.py migrate` runs automatically
4. Gunicorn starts with 2 workers bound to `$PORT`

The Railway health check hits `GET /up`.

---

## Database Notes

- **Local:** SQLite — zero config, auto-created on first `migrate`
- **Production:** MySQL 9.4+ — PyMySQL with the `cryptography` package handles `caching_sha2_password` natively (no SSL/RSA workarounds needed)

---

## Running with Docker locally

```bash
docker build -t finances-api .

docker run -p 8000:8000 \
  -e SECRET_KEY=local-secret \
  -e DEBUG=True \
  finances-api
```

> Without `DB_HOST`, the container will use SQLite.
