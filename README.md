# sniptw

A high-performance URL shortener with a CLI-first design. Built with FastAPI, PostgreSQL, and async Python.

**Live Demo:** https://sniptw-production.up.railway.app

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [CLI Reference](#cli-reference)
- [API Reference](#api-reference)
- [Database Schema](#database-schema)
- [Testing](#testing)
- [Deployment](#deployment)
- [License](#license)

---

## Overview

sniptw is a URL shortening service designed for both programmatic and command-line use. It provides:

- Short URL generation with custom or auto-generated slugs
- Password-protected links
- Configurable link expiration
- Click analytics with geographic and device tracking
- JWT-based authentication
- Full async I/O for high concurrency

The project follows a layered architecture with clear separation between API routes, business logic, and data access.

---

## Architecture

```
sniptw/
├── backend/
│   └── app/
│       ├── api/v1/
│       │   ├── routes/          # HTTP endpoints
│       │   └── dependencies.py  # Dependency injection
│       ├── core/
│       │   ├── config.py        # Application settings
│       │   └── security.py      # Password hashing, JWT
│       ├── db/
│       │   ├── models/          # SQLAlchemy ORM models
│       │   ├── repositories/    # Data access layer
│       │   ├── base.py          # Database engine
│       │   └── session.py       # Session management
│       ├── schemas/             # Pydantic request/response models
│       ├── services/            # Business logic layer
│       └── main.py              # FastAPI application
├── cli/
│   └── sniptw/
│       ├── commands/            # CLI command groups
│       ├── client.py            # HTTP client for API
│       ├── config.py            # CLI configuration
│       └── __init__.py          # Typer application
├── alembic/                     # Database migrations
└── tests/
    ├── unit/                    # Unit tests
    └── integration/             # Integration tests
```

### Design Principles

**Repository Pattern:** Data access is abstracted through repository classes, isolating database operations from business logic.

**Service Layer:** All business rules live in service classes. Routes are thin handlers that delegate to services.

**Dependency Injection:** FastAPI's dependency system manages database sessions, authentication, and service instantiation.

**Async Throughout:** All I/O operations use async/await for non-blocking execution.

---

## Technology Stack

### Runtime

| Component | Technology | Purpose |
|-----------|------------|---------|
| Language | Python 3.14+ | Runtime environment |
| Web Framework | FastAPI | Async HTTP API |
| ORM | SQLAlchemy 2.0 | Async database access |
| Database | PostgreSQL | Primary data store |
| Cache | Redis | Session and rate limit storage |
| Migrations | Alembic | Schema versioning |

### Security

| Component | Technology | Purpose |
|-----------|------------|---------|
| Password Hashing | bcrypt | Secure password storage |
| Authentication | python-jose | JWT token generation and validation |
| HTTPS | Uvicorn + Reverse Proxy | Transport encryption |

### CLI

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | Typer | Command-line interface |
| Output | Rich | Formatted terminal output |
| HTTP Client | httpx | API communication |

### Development

| Component | Technology | Purpose |
|-----------|------------|---------|
| Package Manager | uv | Dependency management |
| Testing | pytest + pytest-asyncio | Test execution |
| Linting | Ruff | Code quality |
| Pre-commit | pre-commit | Git hooks |

### Deployment

| Component | Technology | Purpose |
|-----------|------------|---------|
| Container | Docker | Application packaging |
| Platform | Railway | Cloud hosting |
| Build | Hatchling | Python package building |

---

## Installation

### Prerequisites

- Python 3.14 or higher
- PostgreSQL 16+
- Redis 7+ (optional, for caching)
- uv package manager

### Local Setup

Clone the repository:

```sh
git clone https://github.com/your-username/sniptw.git
cd sniptw
```

Install dependencies:

```sh
uv sync
```

Set up the database:

```sh
# Start PostgreSQL and Redis via Docker
docker compose up -d

# Run migrations
uv run alembic upgrade head
```

Start the development server:

```sh
uv run fastapi dev backend/app/main.py
```

The API will be available at `http://localhost:8000`.

---

## Configuration

Configuration is managed through environment variables. Create a `.env` file in the project root:

```sh
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/sniptw

# Redis (optional)
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
BASE_URL=http://localhost:8000
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string with asyncpg driver |
| `REDIS_URL` | No | `redis://localhost:6379` | Redis connection string |
| `SECRET_KEY` | Yes | - | JWT signing key (minimum 32 characters) |
| `ALGORITHM` | No | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | Token validity period |
| `BASE_URL` | No | `http://localhost:8000` | Public URL for generated links |

---

## CLI Reference

The CLI communicates with the API over HTTP. Configuration is stored in `~/.config/sniptw/`.

### Global Commands

```sh
# Display help
sniptw --help

# Show version
sniptw version

# Configure API endpoint
sniptw config --api-url https://sniptw-production.up.railway.app
sniptw config --show

# Quick URL shortening (requires authentication)
sniptw shorten https://example.com
```

### Authentication

```sh
# Register a new account
sniptw auth register
sniptw auth register --email user@example.com --username myuser --password secret

# Login and store token
sniptw auth login
sniptw auth login --username user@example.com --password secret

# Check authentication status
sniptw auth status

# Clear stored credentials
sniptw auth logout
```

### Link Management

```sh
# Create a short link
sniptw links create https://example.com/very/long/url
sniptw links create https://example.com --slug myslug
sniptw links create https://example.com --expires 7
sniptw links create https://example.com --password secret

# List all links
sniptw links list

# Get link details
sniptw links get <slug>

# Update a link
sniptw links update <slug> --url https://new-url.com
sniptw links update <slug> --inactive
sniptw links update <slug> --active

# Delete a link
sniptw links delete <slug>
sniptw links delete <slug> --force
```

### Analytics

```sh
# Get statistics for a link
sniptw analytics stats <slug>
sniptw analytics stats <slug> --limit 50

# Account summary
sniptw analytics summary
```

---

## API Reference

### Base URL

- **Production:** `https://sniptw-production.up.railway.app`
- **Local:** `http://localhost:8000`

### Authentication

The API uses JWT Bearer tokens. Include the token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

### Endpoints

#### Health Check

```
GET /health
```

Returns API status.

**Response:**
```json
{
  "status": "online"
}
```

---

#### Register

```
POST /api/v1/auth/register
Content-Type: application/json
```

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "myusername",
  "password": "securepassword"
}
```

**Response:** `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "myusername",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

#### Login

```
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded
```

Authenticate and receive an access token.

**Request Body:**
```
username=user@example.com&password=securepassword
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

#### Create Link

```
POST /api/v1/links/
Authorization: Bearer <token>
Content-Type: application/json
```

Create a new short link.

**Request Body:**
```json
{
  "original_url": "https://example.com/very/long/url",
  "slug": "custom-slug",
  "expires_in_days": 30,
  "password": "optional-password"
}
```

All fields except `original_url` are optional. If `slug` is omitted, one is generated automatically.

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "slug": "custom-slug",
  "original_url": "https://example.com/very/long/url",
  "click_count": 0,
  "is_active": true,
  "expires_at": "2024-02-14T10:30:00Z",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

#### List Links

```
GET /api/v1/links/
Authorization: Bearer <token>
```

Retrieve all links owned by the authenticated user.

**Response:** `200 OK`
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "slug": "abc123",
    "original_url": "https://example.com",
    "click_count": 42,
    "is_active": true,
    "expires_at": null,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

---

#### Get Link

```
GET /api/v1/links/{slug}
```

Retrieve link details by slug. Does not require authentication.

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "slug": "abc123",
  "original_url": "https://example.com",
  "click_count": 42,
  "is_active": true,
  "expires_at": null,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

#### Update Link

```
PATCH /api/v1/links/{slug}
Authorization: Bearer <token>
Content-Type: application/json
```

Update link properties. Only the link owner can update.

**Request Body:**
```json
{
  "original_url": "https://new-destination.com",
  "is_active": false
}
```

**Response:** `200 OK`

---

#### Delete Link

```
DELETE /api/v1/links/{slug}
Authorization: Bearer <token>
```

Soft-delete a link. The link becomes inaccessible but data is retained.

**Response:** `204 No Content`

---

#### Redirect

```
GET /{slug}
```

Redirect to the original URL. Increments click counter and records analytics.

**Response:** `302 Found`
```
Location: https://example.com/original/url
```

---

#### Get Analytics

```
GET /api/v1/analytics/{slug}
Authorization: Bearer <token>
```

Retrieve click statistics for a link. Only the link owner can access.

**Response:** `200 OK`
```json
{
  "slug": "abc123",
  "original_url": "https://example.com",
  "total_clicks": 42,
  "clicks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "clicked_at": "2024-01-15T10:30:00Z",
      "country": "United States",
      "device_type": "desktop",
      "referer": "https://twitter.com"
    }
  ]
}
```

---

### Error Responses

All errors follow a consistent format:

```json
{
  "detail": "Error message describing the problem"
}
```

| Status Code | Description |
|-------------|-------------|
| `400` | Bad request (validation error, duplicate email/username) |
| `401` | Unauthorized (missing or invalid token) |
| `403` | Forbidden (insufficient permissions) |
| `404` | Resource not found |
| `409` | Conflict (duplicate slug) |
| `410` | Gone (expired link) |
| `422` | Unprocessable entity (invalid request body) |

---

## Database Schema

### Users

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `email` | VARCHAR | Unique, indexed |
| `username` | VARCHAR | Not null |
| `hashed_password` | VARCHAR | Not null |
| `is_active` | BOOLEAN | Default: true |
| `created_at` | TIMESTAMP | Auto-generated |

### Links

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `slug` | VARCHAR | Indexed |
| `original_url` | VARCHAR(500) | Not null |
| `user_id` | UUID | Foreign key to users |
| `click_count` | INTEGER | Default: 0 |
| `is_active` | BOOLEAN | Default: true |
| `password_hash` | VARCHAR | Nullable |
| `expires_at` | TIMESTAMP | Nullable |
| `created_at` | TIMESTAMP | Auto-generated |

### Clicks

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `link_id` | UUID | Foreign key to links |
| `clicked_at` | TIMESTAMP | Auto-generated |
| `country` | VARCHAR | Nullable |
| `device_type` | VARCHAR | Nullable |
| `referer` | VARCHAR | Nullable |
| `ip_hash` | VARCHAR | SHA-256 of client IP |

---

## Testing

### Running Tests

```sh
# Run all tests
uv run pytest

# Run unit tests only (no database required)
uv run pytest tests/unit/ -v

# Run integration tests (requires test database)
uv run pytest tests/integration/ -v

# Run with coverage
uv run pytest --cov=backend --cov-report=html
```

### Test Structure

**Unit Tests:** Test isolated functions without external dependencies. Located in `tests/unit/`.

- `test_security.py`: Password hashing, JWT token generation

**Integration Tests:** Test full request/response cycles with a test database. Located in `tests/integration/`.

- `test_auth.py`: Registration, login flows
- `test_links.py`: CRUD operations, redirects
- `test_analytics.py`: Statistics retrieval

### Test Database

Integration tests require a PostgreSQL database. Set the connection string:

```sh
export TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/sniptw_test
```

---

## Deployment

### Docker

Build the image:

```sh
docker build -t sniptw .
```

Run with environment variables:

```sh
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db \
  -e SECRET_KEY=your-secret-key \
  sniptw
```

### Docker Compose

For local development with all services:

```sh
docker compose up -d
```

This starts PostgreSQL and Redis containers with health checks.

### Railway

The project includes Railway-compatible configuration. Deploy directly from the repository:

1. Connect your GitHub repository to Railway
2. Set the required environment variables (`DATABASE_URL`, `SECRET_KEY`)
3. Railway will detect the Dockerfile and deploy automatically

### Production Checklist

- [ ] Set a strong `SECRET_KEY` (minimum 32 characters)
- [ ] Use a managed PostgreSQL instance
- [ ] Configure HTTPS via reverse proxy or platform
- [ ] Set appropriate `ACCESS_TOKEN_EXPIRE_MINUTES`
- [ ] Run database migrations: `alembic upgrade head`

---

## License

MIT License. See [LICENSE](LICENSE) for details.
