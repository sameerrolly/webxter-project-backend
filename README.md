# Django REST Framework Backend

Production-ready Django backend with JWT authentication, designed to pair with a React/Next.js frontend (Vite dev server on `http://localhost:5173`).

---

## Stack

| Layer | Library |
|---|---|
| Framework | Django 5 + Django REST Framework |
| Auth | `djangorestframework-simplejwt` |
| CORS | `django-cors-headers` |
| Config | `python-decouple` |
| Static files | `whitenoise` |
| Images | `Pillow` |
| Production server | `gunicorn` |

---

## Project Structure

```
backend/
├── core/                   # Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── accounts/           # Custom user model, JWT auth, profile
│   ├── projects/           # Projects CRUD (protected)
│   └── orders/             # Orders CRUD (protected)
├── media/                  # User-uploaded files (git-ignored)
├── staticfiles/            # Collected static files (git-ignored)
├── .env                    # Local environment variables (git-ignored)
├── .env.example            # Template — copy to .env
├── manage.py
└── requirements.txt
```

---

## Quick Start

### 1. Clone & enter the directory

```bash
cd backend
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env and set a strong SECRET_KEY
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create a superuser (optional)

```bash
python manage.py createsuperuser
```

### 7. Start the development server

```bash
python manage.py runserver
```

The API is now available at `http://127.0.0.1:8000`.

---

## API Endpoints

### Auth  `/api/v1/auth/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/register/` | Public | Create account, returns tokens |
| POST | `/login/` | Public | Login, returns tokens + user info |
| POST | `/token/refresh/` | Public | Refresh access token |
| POST | `/logout/` | Required | Blacklist refresh token |
| GET | `/profile/` | Required | Get current user profile |
| PATCH | `/profile/` | Required | Update profile |
| POST | `/change-password/` | Required | Change password |

### Projects  `/api/v1/projects/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | Required | List own projects |
| POST | `/` | Required | Create project |
| GET | `/<id>/` | Required | Get project |
| PATCH | `/<id>/` | Required | Update project |
| DELETE | `/<id>/` | Required | Delete project |

### Orders  `/api/v1/orders/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | Required | List own orders |
| POST | `/` | Required | Create order |
| GET | `/<id>/` | Required | Get order |
| PATCH | `/<id>/` | Required | Update order |
| DELETE | `/<id>/` | Required | Delete order |

---

## Authentication Flow

All protected endpoints require the `Authorization` header:

```
Authorization: Bearer <access_token>
```

**Register:**
```json
POST /api/v1/auth/register/
{
  "email": "user@example.com",
  "first_name": "Jane",
  "last_name": "Doe",
  "password": "StrongPass123!",
  "password2": "StrongPass123!"
}
```

**Login:**
```json
POST /api/v1/auth/login/
{
  "email": "user@example.com",
  "password": "StrongPass123!"
}
```

Response includes `access`, `refresh`, and `user` object.

**Refresh:**
```json
POST /api/v1/auth/token/refresh/
{
  "refresh": "<refresh_token>"
}
```

---

## Production Deployment

```bash
# Collect static files
python manage.py collectstatic --noinput

# Run with gunicorn
gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

Set in `.env` for production:
```
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
SECRET_KEY=<long-random-string>
CORS_ALLOWED_ORIGINS=https://yourfrontend.com
```

---

## Admin Panel

Available at `/admin/` — log in with your superuser credentials.
