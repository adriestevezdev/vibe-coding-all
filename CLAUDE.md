# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Primary Development (Docker Compose - Recommended)
```bash
# Start all services (frontend:3000, backend:8000, db:5432, adminer:8080)
docker compose up

# Start specific services
docker compose up frontend backend db

# View service logs
docker compose logs -f backend
docker compose logs -f frontend

# Stop all services
docker compose down
```

### Manual Development
**Frontend (Next.js):**
```bash
cd frontend
npm install
npm run dev          # Development server
npm run build        # Production build
npm run lint         # ESLint
```

**Backend (FastAPI):**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Database Management
```bash
# Access PostgreSQL via Docker
docker-compose exec db psql -U postgres -d vibe_coding

# Access Adminer web interface
open http://localhost:8080
```

### Testing
```bash
cd backend
pytest                    # Run all tests
pytest tests/test_auth.py  # Run specific test file
pytest -v                 # Verbose output
pytest --cov             # Coverage report
```

### Code Quality (Backend)
```bash
cd backend
black .                   # Code formatting
isort .                   # Import sorting
flake8                    # Linting
```

## Architecture Overview

This is a full-stack SaaS application that transforms project ideas into structured documentation using AI.

### Technology Stack
- **Frontend**: Next.js 15 + React 19 + TypeScript + Tailwind CSS
- **Backend**: FastAPI + SQLAlchemy + AsyncPG + PostgreSQL
- **AI**: OpenAI API integration (GPT-4)
- **Auth**: JWT tokens with bcrypt password hashing
- **Infrastructure**: Docker + Docker Compose

### Key Architectural Patterns

**Backend Structure (FastAPI):**
- `app/main.py` - Main FastAPI application with CORS middleware
- `app/database.py` - Async SQLAlchemy engine and session management
- `app/core/` - Configuration, security, logging utilities
- `app/models/` - SQLAlchemy ORM models (User, Project, Prompt, PromptVersion, Subscription)
- `app/routers/` - API route handlers organized by domain
- `app/services/` - Business logic (OpenAI integration, auth, CRUD operations)
- `app/schemas/` - Pydantic models for request/response validation

**Database Schema:**
- UUID primary keys across all tables
- User -> Projects (1:many) -> Prompts (1:many) -> PromptVersions (1:many)
- Subscription model ready for SaaS billing integration
- Automatic `updated_at` timestamps with triggers

**Frontend Structure (Next.js App Router):**
- `src/app/` - App Router pages and layouts
- `src/components/` - Reusable React components
- `src/contexts/AuthContext.tsx` - Global authentication state
- `services/api.ts` - Centralized API client with token management
- `types/` - TypeScript definitions matching backend schemas

**Authentication Flow:**
- JWT tokens with configurable expiry
- Frontend stores tokens in localStorage
- Automatic token inclusion in API requests
- Protected routes using HOCs and dependency injection

**AI Integration:**
- OpenAI service with async client and timeout handling
- Customizable system prompts for "Vibe Coding" style documentation
- Error handling for rate limits and API failures
- Generated content tracking with `generated_at` timestamps

### Database Migrations

Migrations are in `backend/migrations/` and run automatically via Docker:
- `001_initial_schema.sql` - Core tables with proper indexes and constraints
- `002_sample_data.sql` - Development seed data
- `003_add_generated_at_to_prompts.sql` - AI generation tracking

### Environment Configuration

**Backend (.env):**
```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/vibe_coding
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4
DEBUG=true
```

**Frontend (.env.local):**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Service Ports
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Database: localhost:5432
- Adminer: http://localhost:8080

### Common Development Workflows

**Adding New API Endpoints:**
1. Create Pydantic schemas in `app/schemas/`
2. Add route handlers in `app/routers/`
3. Implement business logic in `app/services/`
4. Update database models if needed

**Frontend API Integration:**
1. Update `services/api.ts` with new endpoint functions
2. Add TypeScript types in `types/`
3. Use in components with proper error handling

**Database Changes:**
1. Create new migration file in `backend/migrations/`
2. Follow existing naming convention (###_description.sql)
3. Test with Docker restart to ensure migrations work

### Key Dependencies
- **Backend**: FastAPI, SQLAlchemy, AsyncPG, OpenAI, python-jose, passlib
- **Frontend**: Next.js, React Hook Form, Zod validation, Tailwind CSS
- **Development**: Docker Compose, pytest, black, ESLint