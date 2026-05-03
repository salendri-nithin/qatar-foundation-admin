# Qatar Foundation — Admin Portal Backend

A production-ready Flask REST API for the Admin Portal UI.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.8+ |
| Framework | Flask 3.x |
| ORM | SQLAlchemy via Flask-SQLAlchemy |
| Auth | JWT via Flask-JWT-Extended |
| Password hashing | bcrypt via Flask-Bcrypt |
| Database | SQLite (dev) / PostgreSQL (prod) |
| CORS | Flask-CORS |

---

## Project Structure

```
qatar_foundation_admin/
├── app.py                          # App factory & entry point
├── config.py                       # Environment-based configuration
├── extensions.py                   # Shared Flask extensions (db, jwt, bcrypt, cors)
├── requirements.txt
├── .env                            # Environment variables (never commit this)
│
├── models/
│   ├── __init__.py
│   ├── admin.py                    # Admin table
│   ├── opportunity.py              # Opportunity table
│   └── reset_token.py             # PasswordResetToken table
│
├── routes/
│   ├── __init__.py
│   ├── auth_routes.py              # /api/auth/*
│   └── opportunity_routes.py      # /api/opportunities/*
│
├── services/
│   ├── __init__.py
│   ├── auth_service.py             # Auth business logic
│   └── opportunity_service.py     # Opportunity business logic
│
└── utils/
    ├── __init__.py
    ├── validators.py               # Input validation helpers
    └── responses.py               # Standardized JSON responses
```

---

## Setup & Run

```bash
# 1. Clone and enter the directory
git clone https://github.com/Neerajvs32/Test1
cd qatar_foundation_admin

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env .env.local               # Edit values as needed

# 5. Run the server
python app.py
# → http://localhost:5000
```

---

## API Reference

All endpoints return JSON. Protected endpoints require:
```
Authorization: Bearer <access_token>
```

### Health

| Method | Endpoint | Auth |
|---|---|---|
| GET | `/api/health` | ❌ |

---

### Auth

#### POST `/api/auth/signup`
```json
{
  "full_name": "Ahmed Al-Rashid",
  "email": "ahmed@qf.org.qa",
  "password": "SecurePass@123",
  "confirm_password": "SecurePass@123"
}
```
**201 Created**
```json
{
  "status": "success",
  "message": "Account created successfully. Please log in.",
  "data": { "id": 1, "full_name": "Ahmed Al-Rashid", "email": "ahmed@qf.org.qa", "created_at": "..." }
}
```

---

#### POST `/api/auth/login`
```json
{
  "email": "ahmed@qf.org.qa",
  "password": "SecurePass@123",
  "remember_me": false
}
```
**200 OK**
```json
{
  "status": "success",
  "message": "Login successful.",
  "data": {
    "access_token": "<jwt>",
    "token_type": "Bearer",
    "expires_in": 3600,
    "admin": { ... }
  }
}
```

---

#### POST `/api/auth/forgot-password`
```json
{ "email": "ahmed@qf.org.qa" }
```
Always returns **200 OK** (prevents email enumeration).
Reset link is printed to the server console.

---

#### POST `/api/auth/reset-password`
```json
{
  "token": "<reset-token-from-console>",
  "new_password": "NewPass@456",
  "confirm_password": "NewPass@456"
}
```

---

### Opportunities (all require JWT)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/opportunities` | List all for logged-in admin |
| POST | `/api/opportunities` | Create a new opportunity |
| GET | `/api/opportunities/<id>` | Get single opportunity |
| PUT | `/api/opportunities/<id>` | Update opportunity |
| DELETE | `/api/opportunities/<id>` | Delete opportunity |

#### Opportunity payload (POST / PUT)
```json
{
  "name": "AI Research Internship",
  "duration": "3 months",
  "start_date": "2025-09-01",
  "description": "Work on cutting-edge AI research projects.",
  "skills": "Python, Machine Learning, PyTorch",
  "category": "Technology",
  "future_opportunities": "Full-time role possible.",
  "max_applicants": 20
}
```
Valid categories: `Technology`, `Business`, `Design`, `Marketing`, `Data Science`, `Other`

---

## Security Highlights

- Passwords are hashed with **bcrypt** — never stored in plain text.
- JWT tokens are stateless and signed with a secret key.
- `remember_me` extends token expiry from 1 hour → 7 days.
- Forgot-password always returns success to prevent **email enumeration**.
- Reset tokens are single-use, expire in **1 hour**, and are invalidated on use.
- Each admin can only access **their own** opportunities — enforced at service layer.
- Generic `"Invalid email or password"` error on login — never reveals which field is wrong.

---

## Postman

Import `Qatar_Foundation_API.postman_collection.json` into Postman.
The Login request auto-saves the JWT token into `{{TOKEN}}` for all subsequent requests.
