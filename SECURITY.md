# Nexus Career AI - Security & Privacy Strategy

This document outlines the comprehensive security architecture and privacy standards for Nexus Career AI. As a SaaS handling sensitive career data (resumes, salaries, employment history), security is a foundational requirement, not an afterthought.

## 1. Data Isolation & Access Control

We adhere to a **"Zero Trust"** database architecture using Supabase Row Level Security (RLS).

### 1.1 Row Level Security (RLS)
*   **Principle**: The database application logic (PostgreSQL) enforces access control, not just the API layer.
*   **Implementation**:
    *   All tables must have `ENABLE ROW LEVEL SECURITY` active.
    *   **Users**: Can only `SELECT` and `UPDATE` their own profile (`auth.uid() = id`).
    *   **Resumes/Jobs/Applications**: Can only be accessed if the `user_id` column matches `auth.uid()`.
    *   **Service Role**: The backend API uses the Service Role Key only when absolutely necessary (e.g., background jobs). For user-initiated requests, it forwards the user's JWT to respect RLS or explicitly filters by `user_id`.

### 1.2 Multi-Tenant Isolation
*   Although all data resides in a single database, logical isolation is enforced via the `user_id` foreign key on all major entities.
*   **Audit**: Regular automated tests verify that User A cannot fetch User B's resumes.

## 2. Secure File Storage

Resume files (PDFs) are stored in Supabase Storage with strict bucket policies.

### 2.1 Storage Policies
*   **Bucket**: `resumes` (Private)
*   **Upload (INSERT)**:
    *   Authenticated users only.
    *   File size limit: **5MB**.
    *   MIME type restriction: `application/pdf` only.
    *   Path convention: `{user_id}/{resume_id}.pdf` (Enforces ownership via path structure).
*   **Read (SELECT)**:
    *   Restricted to the file owner via RLS policy `bucket_id = 'resumes' AND (storage.foldername(name))[1] = auth.uid()::text`.
*   **Delete**: Owner only.

### 2.2 Access Patterns
*   **Public Access**: DISABLED. Files are never publicly addressable.
*   **Backend Access**: The FastAPI backend generates **Signed URLs** with short expiration times (e.g., 60 seconds) when the parsing service needs to read a file, or when the frontend needs to render the PDF viewer.

## 3. Authentication & Token Handling

We use Supabase Auth (GoTrue) for identity management.

### 3.1 Frontend (Next.js)
*   **Storage**: We utilize `@supabase/ssr` to store session tokens in **HttpOnly, Secure, SameSite=Lax Cookies**.
    *   *Why*: Prevents XSS attacks from stealing tokens (unlike `localStorage`).
*   **CSRF Protection**: Next.js App Router's server actions and API routes automatically handle CSRF protection for cookie-based requests.

### 3.2 Backend (FastAPI)
*   **Validation**: Every protected endpoint relies on a `get_current_user` dependency.
*   **Mechanism**:
    1.  Extract `Bearer` token from `Authorization` header.
    2.  Verify JWT signature using Supabase's project secret (HS256).
    3.  Validate `exp` (expiration) and `aud` (audience).
    4.  Extract `sub` (Subject ID / User ID).
*   **Context**: The `user_id` is injected into the request context for logging and logic.

## 4. Rate Limiting & Abuse Prevention

To protect resources and prevent scraping/abuse.

### 4.1 Implementation Strategy
*   **Tool**: `fastapi-limiter` (backed by Redis).
*   **Identification**: Rate limits are applied per `user_id` (for auth users) or `IP address` (for anon).

### 4.2 Policies
| Endpoint Scope | Limit (Free Tier) | Limit (Pro Tier) | Action |
| :--- | :--- | :--- | :--- |
| **Global API** | 60 req/min | 300 req/min | 429 Too Many Requests |
| **Auth (Login/Signup)** | 5 req/min | 5 req/min | 429 + IP Ban (Temp) |
| **Resume Analysis (AI)** | 5 / day | 50 / day | 429 Upgrade Prompt |
| **PDF Export** | 10 / day | Unlimited | 429 Upgrade Prompt |

## 5. GDPR & Privacy Compliance

We are proactive about user privacy rights.

### 5.1 Right to Access (Data Portability)
*   **Endpoint**: `GET /api/v1/user/export`
*   **Function**: Aggregates all user data (Profile, Resumes, Jobs, Analysis Logs) into a single JSON bundle and generates download links for stored files.

### 5.2 Right to be Forgotten (Deletion)
*   **Endpoint**: `DELETE /api/v1/user/me` (Requires strict re-authentication or "sudo" mode).
*   **Mechanism**:
    1.  Delete User record in `auth.users`.
    2.  **Cascading Deletion**: Postgres `ON DELETE CASCADE` automatically removes profile, resumes, jobs, and analysis.
    3.  **Storage Cleanup**: A Database Trigger invokes a specialized Edge Function to delete the user's folder in Supabase Storage.

### 5.3 Data Minimization
*   We only store the **parsed text** necessary for ATS matching.
*   Original PDFs are stored, but intermediate processing artifacts (temp images, raw OCR buffers) are discarded immediately after processing.
*   **AI Data Usage**: We strictly use **Zero-Retention** settings on Gemini API calls where possible. User data is sent for inference and the response is stored, but the input data is not used to train Google's models (Enterprise/Paid API tier guarantees).

## 6. Infrastructure Security

*   **HTTPS**: Enforced everywhere. HSTS enabled.
*   **Dependency Scanning**: Weekly audits of `npm` and `pip` packages for vulnerabilities (e.g., Dependabot).
*   **Logging**: Sensitive PII (emails, phone numbers) is masked in server logs.

## 7. Implementation Checklist

- [ ] **Database**: Audit RLS policies on all tables.
- [ ] **Storage**: Create 'resumes' bucket and apply RLS policies.
- [ ] **Backend**: Install `fastapi-limiter` and configure Redis connection.
- [ ] **Backend**: Implement `verify_token` dependency in FastAPI.
- [ ] **Backend**: Create `PrivacyService` for Export/Delete logic.
- [ ] **Frontend**: Configure `@supabase/ssr` for HttpOnly cookies.
