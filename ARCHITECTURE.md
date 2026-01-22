# Nexus Career AI - System Architecture

## 1. Executive Summary

Nexus Career AI is a production-grade SaaS application designed to optimize resumes for tech professionals using advanced AI. The system adopts a **Service-Oriented Architecture (SOA)** approach, leveraging a decoupled frontend and backend to ensure scalability, maintainability, and security.

**Core Philosophy:** "Security-First, AI-Driven, Scalable."

---

## 2. High-Level Architecture Diagram

```mermaid
graph TD
    User[User (Browser)] -->|HTTPS| CDN[CDN / Edge Network]
    CDN -->|Next.js App| Frontend[Frontend (Next.js 15)]
    
    subgraph "Client Layer"
        Frontend -->|Auth (JWT)| AuthProvider[Supabase Auth]
        Frontend -->|API Requests| Backend[Backend API (FastAPI)]
        Frontend -->|File Uploads| Storage[Supabase Storage]
    end

    subgraph "Backend Layer (Python)"
        Backend -->|Verify Token| AuthProvider
        Backend -->|Read/Write Data| DB[(PostgreSQL - Supabase)]
        Backend -->|Prompt & Context| AI[Gemini 2.0 Flash]
        Backend -->|Parse/Process| Parser[Resume Parser Service]
    end

    subgraph "Data Layer"
        DB -->|Row Level Security| AuthProvider
        Storage -->|Policies| AuthProvider
    end
```

---

## 3. Component Responsibilities

### 3.1 Frontend (Next.js 15 App Router)
*   **Role:** The presentation layer and orchestration of user interactions.
*   **Responsibilities:**
    *   **Rendering:** Server-Side Rendering (SSR) for initial load performance and SEO; Client-Side Rendering (CSR) for interactive dashboards.
    *   **State Management:** Managing local UI state (forms, modals) and server state (user data, resume lists) using **React Query** (or SWR) + **Zustand**.
    *   **Authentication:** Handling user sessions via `@supabase/ssr`. Protecting routes via Middleware.
    *   **Direct Uploads:** Facilitating secure, direct-to-cloud file uploads to Supabase Storage to offload bandwidth from the backend.

### 3.2 Backend (Python FastAPI)
*   **Role:** The intelligence engine and business logic enforcer.
*   **Responsibilities:**
    *   **API Gateway:** Exposing RESTful endpoints for the frontend.
    *   **Orchestration:** Managing the flow between database, parsing, and AI services.
    *   **Resume Parsing:** Extracting raw text and structure from PDF/DOCX files.
    *   **AI Integration:** Interfacing with **Gemini 2.0 Flash** for analysis, optimization, and keyword targeting.
    *   **Security:** Validating JWT tokens, rate limiting, and input sanitization (Pydantic).

### 3.3 Database (PostgreSQL via Supabase)
*   **Role:** The single source of truth for structured data.
*   **Responsibilities:**
    *   **User Data:** Profiles, settings, subscription status.
    *   **Resume Data:** Metadata, raw extracted text, optimized versions, analysis scores.
    *   **Security:** Enforcing **Row Level Security (RLS)** policies to ensure users can only access their own data.

### 3.4 Authentication & Authorization (Supabase Auth)
*   **Role:** Identity management.
*   **Flow:**
    1.  User signs up/logs in via Frontend (Email/Password or OAuth).
    2.  Supabase issues a JWT (Access Token).
    3.  Frontend includes JWT in Authorization header for Backend requests.
    4.  Backend validates JWT signature and extracts User ID.

### 3.5 File Storage (Supabase Storage)
*   **Role:** Secure object storage for binary files.
*   **Flow:**
    *   **Upload:** Frontend requests a signed URL or uploads directly using Supabase SDK (governed by RLS policies).
    *   **Access:** Backend accesses files via internal secure URLs for processing.

### 3.6 AI Processing (Gemini 2.0 Flash)
*   **Role:** The core value proposition engine.
*   **Flow:**
    1.  **Context Construction:** Backend assembles a prompt containing the Resume Text + Job Description (if provided) + Optimization Rules.
    2.  **Inference:** Request sent to Gemini 2.0 Flash.
    3.  **Structured Output:** AI returns JSON-structured data (improved bullet points, skills gap analysis, formatting suggestions).
    4.  **Persistence:** Backend saves the result to PostgreSQL.

---

## 4. Key Data Flows

### 4.1 Resume Upload & Optimization Flow
1.  **Upload:** User uploads PDF on Frontend -> stored in Supabase Storage.
2.  **Trigger:** Frontend calls `POST /api/resumes/analyze` with file path.
3.  **Processing (Backend):**
    *   Downloads file stream from Storage.
    *   Parses text (e.g., using `pypdf` or `unstructured`).
    *   Constructs prompt for Gemini.
    *   Calls Gemini API.
4.  **Storage:** Saves analysis results to `resumes` table.
5.  **Response:** Returns analysis ID to Frontend.
6.  **Update:** Frontend polls or receives real-time update (via Supabase Realtime) to display results.

---

## 5. Security & Scalability

*   **Security:**
    *   **RLS:** Database-level security is paramount.
    *   **Input Validation:** Strict Pydantic models for all API inputs.
    *   **Environment Variables:** Secrets managed strictly via `.env` files (never committed).
*   **Scalability:**
    *   **Stateless Backend:** FastAPI is stateless, allowing horizontal scaling (e.g., via Docker/Kubernetes).
    *   **Serverless Database:** Supabase manages DB scaling.
    *   **Async Processing:** Heavy AI tasks handled asynchronously (using `asyncio` or background tasks).
