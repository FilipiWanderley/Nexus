# Nexus Career AI - Deployment & Portfolio Strategy

This document outlines the strategy for deploying Nexus Career AI to production and presenting it effectively to technical recruiters.

## 1. Deployment Architecture

We utilize a modern **"Vercel + Railway + Supabase"** stack, which is industry-standard for high-performance SaaS applications.

### 1.1 Frontend (Next.js) -> Vercel
*   **Platform**: Vercel
*   **Reason**: Native support for Next.js App Router, Edge Functions, and Image Optimization.
*   **Build Command**: `npm run build`
*   **Environment Variables**:
    *   `NEXT_PUBLIC_SUPABASE_URL`
    *   `NEXT_PUBLIC_SUPABASE_ANON_KEY`
    *   `NEXT_PUBLIC_API_URL` (Backend URL)

### 1.2 Backend (FastAPI) -> Railway
*   **Platform**: Railway (Recommended) or Render.
*   **Reason**: Excellent Docker container support, automatic builds from GitHub, and internal networking capabilities.
*   **Configuration**:
    *   **Dockerfile**: Python 3.11-slim base.
    *   **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
*   **Environment Variables**:
    *   `SUPABASE_URL`
    *   `SUPABASE_KEY` (Service Role)
    *   `GEMINI_API_KEY`
    *   `BACKEND_CORS_ORIGINS` (Set to Vercel Frontend URL)

### 1.3 Database & Storage -> Supabase
*   **Platform**: Supabase Managed Cloud.
*   **Assets**:
    *   **PostgreSQL**: Primary data store.
    *   **Auth**: User identity management.
    *   **Storage**: Resume PDF buckets.

## 2. Environment Separation

To demonstrate professional SDLC (Software Development Life Cycle) practices:

*   **Production Environment (`main` branch)**
    *   URL: `nexus-career-ai.vercel.app`
    *   Database: `prod-db` (Supabase Project A)
    *   Stable, optimized, no debug logs.

*   **Development Environment (`develop` branch)**
    *   URL: `dev-nexus-career-ai.vercel.app`
    *   Database: `dev-db` (Supabase Project B - *Optional for portfolio, but recommended*)
    *   Enables testing features without breaking the live demo.

## 3. Demo Strategy (The "Hero Path")

Recruiters spend < 60 seconds on a portfolio project. The demo must be flawless and frictionless.

### 3.1 The "No-Login" Friction Reducer
*   **Strategy**: Provide a "Try Demo Mode" button that logs them in as a pre-seeded user (`recruiter@demo.com` / `password123`).
*   **Pre-loaded Data**:
    *   1 Resume (Software Engineer).
    *   1 Job Description (Google Senior SWE).
    *   Analysis Result: 72/100 Score.
    *   *Why*: Lets them see the value immediately without uploading files.

### 3.2 The Script
1.  **Landing Page**: clear value prop ("Beat the ATS with AI").
2.  **Dashboard**: Visual "Score Gauge" (Green/Yellow/Red).
3.  **Optimization Action**: Click "Fix Bullet Point" -> Watch AI rewrite it in real-time -> Score goes up.
4.  **Export**: Download the PDF.

## 4. Portfolio Presentation (GitHub & LinkedIn)

### 4.1 GitHub README Checklist
A generic README gets ignored. Yours must look like an open-source library documentation.

- [ ] **Badges**: CI/CD Passing, Python 3.11, Next.js 14, License.
- [ ] **Architecture Diagram**: Embed the Mermaid chart from `ARCHITECTURE.md`.
- [ ] **"How I Built This" Section**:
    *   *Challenge*: "AI Hallucinations in Resumes."
    *   *Solution*: "Implemented a constraint-based prompt engineering system with separate validation layers."
    *   *Challenge*: "Secure Data Access."
    *   *Solution*: "Row Level Security (RLS) policies at the database level, ensuring zero-leakage multi-tenancy."
- [ ] **Local Setup**: One-command setup (`docker-compose up` or `make install`).

### 4.2 LinkedIn Post Strategy
**Hook**: "I built an ATS Optimizer that actually respects the truth. Here's the engineering behind Nexus Career AI."

**Content Pillars**:
1.  **System Design**: "Instead of a monolithic script, I built a layered SOA with FastAPI and Next.js."
2.  **AI Engineering**: "Gemini 2.0 is powerful, but it lies. I built a 'Fact-Preservation' layer that forces the model to strictly adhere to the user's employment history."
3.  **Security**: "Implemented RLS policies to ensure candidates' salary data is cryptographically isolated."

**Assets**:
*   Short video (30s) showing the "Rewrite" feature.
*   Screenshot of the Architecture Diagram.
*   Link to live demo.

## 5. Next Steps for You

1.  **Dockerize Backend**: Ensure `Dockerfile` is production-ready.
2.  **Seed Data**: Create the `seed_data.py` script for the demo user.
3.  **Record Demo**: Use Loom or OBS.
