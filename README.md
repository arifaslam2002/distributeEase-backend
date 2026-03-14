# distributeEase — Backend API

A FastAPI + PostgreSQL backend for a distribution management system with role-based access control, order management, and Telegram notifications.

---

## Tech Stack

| Technology | Purpose |
|---|---|
| FastAPI | Web framework |
| PostgreSQL | Database |
| SQLAlchemy | ORM |
| bcrypt | Password hashing |
| python-jose | JWT authentication |
| Telegram Bot API | Order notifications |
| Uvicorn | ASGI server |

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI app, CORS, router registration
│   ├── db/
│   │   ├── base.py              # Shared SQLAlchemy Base
│   │   └── session.py           # Database engine, session, create_tables
│   ├── models/
│   │   ├── user.py
│   │   ├── shop.py
│   │   ├── product.py
│   │   ├── order.py
│   │   └── order_item.py
│   ├── schemas/
│   │   ├── user_schema.py
│   │   ├── shop_schema.py
│   │   ├── product_schema.py
│   │   └── order_schema.py
│   └── routers/
│       ├── auth_router.py
│       ├── shop_router.py
│       ├── product_router.py
│       ├── order_router.py
│       └── user_router.py
├── core/
│   ├── security.py              # JWT, password hashing
│   ├── dependencies.py          # get_current_user, require_roles
│   └── telegram.py              # Telegram notification
├── .env                         # Environment variables
├── requirements.txt
└── myenv/                       # Virtual environment (not in git)
```

---

## Setup — Local Development

### 1. Clone and navigate
```bash
git clone https://github.com/arifaslam2002/distributeease-backend.git
cd distributeease-backend
```

### 2. Create virtual environment
```bash
python -m venv myenv

# Windows
myenv\Scripts\activate

# Mac/Linux
source myenv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create `.env` file
```env
DATABASE_URL=postgresql://user:password@localhost:5432/distributeease
SECRET_KEY=your_secret_key_here
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

> ⚠️ No inline comments in `.env` — they become part of the value.

### 5. Run the server
```bash
uvicorn app.main:app --reload
```

API runs at: `http://localhost:8000`  
Swagger docs: `http://localhost:8000/docs`

---

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing secret (any long random string) |
| `TELEGRAM_TOKEN` | Telegram bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Your Telegram chat/group ID |

---

## API Endpoints

### Auth
| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/auth/register` | Admin | Register new user |
| POST | `/auth/login` | Public | Login, returns JWT |
| GET | `/auth/me` | All | Get current user |
| DELETE | `/auth/user/{id}` | Admin | Delete user |

### Shops
| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/shops/shops` | Admin, Salesman | List shops |
| POST | `/shops/shop` | Admin, Salesman | Add shop |
| PATCH | `/shops/shops/{id}` | Admin, Salesman | Update shop |
| DELETE | `/shops/shop/{id}` | Admin, Salesman | Delete shop |

### Products
| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/products/products` | All | List products |
| POST | `/products/product` | Admin | Add product |
| PATCH | `/products/product/{id}` | Admin | Update product |
| DELETE | `/products/product/{id}` | Admin | Delete product |

### Orders
| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/orders/orders` | All | List all orders |
| POST | `/orders/{shop_id}/order` | Admin, Salesman | Place order |
| GET | `/orders/order/{id}` | All | Get order details |
| GET | `/orders/{shop_id}/order` | Admin, Salesman | Get orders by shop |
| PATCH | `/orders/order/{id}` | Admin, Salesman | Update order |
| DELETE | `/orders/orders/{id}` | Admin | Delete order |
| GET | `/orders/summary/{date}` | All | Daily summary |

### Users
| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/users/users` | Admin | List all users |

---

## Roles

| Role | Access |
|---|---|
| `admin` | Full access — all endpoints |
| `salesman` | Own shops and orders only |
| `packing_team` | View orders and summaries only |

---

## JWT Token

Login returns a token. Include it in all requests:
```
Authorization: Bearer <token>
```

Token payload:
```json
{
  "sub": "user_id",
  "role": "admin",
  "name": "Arif"
}
```

---

## Telegram Notifications

Sent automatically on:
- New order placed
- Daily packing summary fetched

Setup:
1. Message `@BotFather` → `/newbot` → copy token
2. Message your bot → visit `https://api.telegram.org/bot<TOKEN>/getUpdates` → copy chat ID
3. Add both to `.env`

---

## Deployment (Render)

1. Push to GitHub
2. Render → New Web Service → connect repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables in Render dashboard
6. Database: Render PostgreSQL (free) or Supabase

> Use UptimeRobot to ping `https://your-app.onrender.com` every 5 min to prevent sleep.

## Requirements

```
fastapi
uvicorn
sqlalchemy
psycopg2-binary
python-jose[cryptography]
bcrypt==4.0.1
python-dotenv
python-multipart
requests
passlib
pydantic[email]
```
