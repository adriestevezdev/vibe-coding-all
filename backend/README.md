# Vibe Coding Backend

Backend API for Vibe Coding platform built with FastAPI.

## Project Structure

```
backend/
├── app/
│   ├── api/            # API routes/endpoints
│   ├── controllers/    # Business logic
│   ├── core/          # Core utilities (config, security, logging)
│   ├── models/        # Pydantic models and database models
│   ├── database.py    # Database configuration
│   └── main.py        # FastAPI application entry point
├── migrations/        # Alembic database migrations
├── requirements.txt   # Python dependencies
├── alembic.ini       # Alembic configuration
└── .env              # Environment variables
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and configure your environment variables:
```bash
cp .env.example .env
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, you can access:
- Interactive API docs: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc
- OpenAPI schema: http://localhost:8000/openapi.json

## Environment Variables

See `.env.example` for all available configuration options.

## Development

- The application uses FastAPI with async/await support
- Database operations use SQLAlchemy with async support (asyncpg)
- Authentication uses JWT tokens
- Password hashing uses bcrypt
- Logging is handled by Loguru
- CORS is configured to allow requests from the Next.js frontend

## Testing

Run tests with pytest:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=app tests/
```
