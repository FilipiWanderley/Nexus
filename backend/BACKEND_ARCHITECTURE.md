# Nexus Career AI - Backend Architecture

## 1. Architectural Pattern: Layered Architecture

We utilize a **Layered Architecture** (Controller-Service-Repository pattern adapted for FastAPI/Supabase) to ensure separation of concerns, testability, and scalability.

**Flow:** `Request` -> `Router` -> `Service` -> `Repository/Client` -> `Database/AI`

## 2. Directory Structure

```
backend/app/
├── core/                   # Global configs and utilities
│   ├── config.py           # Pydantic Settings (Env vars)
│   ├── security.py         # Auth utilities (JWT validation)
│   ├── exceptions.py       # Custom exception classes
│   └── logging.py          # Structured logging setup
├── api/                    # API Layer (Routers)
│   ├── v1/                 # Versioning
│   │   ├── api.py          # Main router aggregator
│   │   └── endpoints/      # Domain-specific endpoints
│   │       ├── resumes.py
│   │       ├── jobs.py
│   │       └── analyze.py
├── schemas/                # Pydantic Models (Data Validation)
│   ├── common.py           # Shared schemas
│   ├── resume.py           # Request/Response models for Resumes
│   └── analysis.py
├── services/               # Business Logic Layer
│   ├── resume_service.py   # Parsing orchestration
│   ├── ai_service.py       # Gemini interaction
│   └── storage_service.py  # Supabase Storage wrapper
├── clients/                # External Service Adapters
│   ├── supabase.py         # Supabase Client singleton
│   └── gemini.py           # Gemini Client wrapper
└── main.py                 # App entry point
```

---

## 3. Layer Responsibilities

### 3.1 API Layer (`api/`)
*   **Role:** The "Front Desk".
*   **Responsibilities:**
    *   Defining routes (endpoints).
    *   Validating inputs (using Pydantic `schemas`).
    *   Handling HTTP status codes.
    *   Injecting dependencies (`Depends`).
    *   **Crucial:** No complex business logic here. It delegates immediately to `services`.

### 3.2 Service Layer (`services/`)
*   **Role:** The "Brain".
*   **Responsibilities:**
    *   Orchestrating workflows (e.g., "Download file -> Parse text -> Call AI -> Save to DB").
    *   Applying business rules.
    *   Handling domain-specific errors.

### 3.3 Client/Repository Layer (`clients/`)
*   **Role:** The "Toolbox".
*   **Responsibilities:**
    *   Direct interaction with external systems (Supabase DB, Gemini API).
    *   Encapsulating raw API calls so the rest of the app doesn't know the implementation details.

### 3.4 Schemas (`schemas/`)
*   **Role:** The "Contract".
*   **Responsibilities:**
    *   Defining the shape of Requests and Responses.
    *   Sanitizing inputs using Pydantic.

---

## 4. Key Engineering Practices

### 4.1 Dependency Injection (DI)
FastAPI's `Depends` system is used for:
*   **Auth:** Injecting the `current_user` into protected routes.
*   **Services:** Injecting service instances (making testing easier by allowing mock overrides).

### 4.2 Error Handling
*   **Global Exception Handler:** Middleware in `main.py` catches all exceptions.
*   **Custom Exceptions:** Defined in `core/exceptions.py` (e.g., `ResumeParsingError`, `AIModelError`).
*   **Mapping:** Exceptions are mapped to appropriate HTTP status codes (400, 404, 500) with standardized JSON error responses.

### 4.3 Logging Strategy
*   **Structured Logging:** Using `logging` with JSON formatter (for production).
*   **Context:** Logs include `request_id`, `user_id`, and `path` for traceability.
*   **Levels:**
    *   `INFO`: High-level flow (e.g., "Resume analysis started").
    *   `ERROR`: Stack traces and operational failures.

---

## 5. Why this architecture?

1.  **Scalability:** Logic is not trapped in routers; services can be reused by background tasks (Celery/Arq) if needed later.
2.  **Maintainability:** Changing the AI provider (e.g., to OpenAI) only requires updating `clients/gemini.py` and `services/ai_service.py`, leaving the API layer untouched.
3.  **Security:** Auth is enforced centrally via DI in the API layer.
