# Nexus Career AI - REST API Specification

## 1. Authentication
Authentication is handled via the `Authorization` header using Bearer Tokens (Supabase JWTs).
**Header:** `Authorization: Bearer <JWT>`

---

## 2. Resumes Resource
*   **Base Path:** `/api/v1/resumes`

### Endpoints
*   `GET /`
    *   **Description:** List all resumes for the authenticated user.
    *   **Response:** `200 OK` `[ { "id": "uuid", "file_name": "MyCV.pdf", "created_at": "..." } ]`
*   `POST /`
    *   **Description:** Register a new resume (after file upload to Storage).
    *   **Body:** `{ "file_path": "resumes/uid/file.pdf", "file_name": "MyCV.pdf" }`
    *   **Response:** `201 Created` `{ "id": "uuid", "status": "processing" }`
*   `GET /{resume_id}`
    *   **Description:** Get resume details and parsed content.
    *   **Response:** `200 OK` `{ "parsed_content": { ... }, "raw_text": "..." }`
*   `DELETE /{resume_id}`
    *   **Description:** Delete resume and associated file.
    *   **Response:** `204 No Content`

---

## 3. Job Descriptions Resource (Kanban)
*   **Base Path:** `/api/v1/jobs`

### Endpoints
*   `GET /`
    *   **Description:** List all tracked jobs (supports filtering by status).
    *   **Query Params:** `?status=applied`
    *   **Response:** `200 OK` `[ { "id": "uuid", "title": "Senior Dev", "company": "Google", "status": "applied" } ]`
*   `POST /`
    *   **Description:** Add a new job to track.
    *   **Body:** `{ "title": "Senior Dev", "company": "Google", "raw_text": "..." }`
    *   **Response:** `201 Created`
*   `PATCH /{job_id}`
    *   **Description:** Update job status (Kanban move).
    *   **Body:** `{ "status": "interviewing" }`
    *   **Response:** `200 OK`

---

## 4. Analysis & AI Resource
*   **Base Path:** `/api/v1/analyses`

### Endpoints
*   `POST /`
    *   **Description:** Trigger a new AI analysis (Resume vs Job).
    *   **Body:** `{ "resume_id": "uuid", "job_description_id": "uuid" }`
    *   **Response:** `201 Created` `{ "id": "uuid", "status": "analyzing" }`
*   `GET /{analysis_id}`
    *   **Description:** Get full analysis results (Score, Summary).
    *   **Response:** `200 OK` `{ "match_score": 85, "summary": "Strong fit..." }`
*   `GET /{analysis_id}/gaps`
    *   **Description:** Get missing keywords.
    *   **Response:** `200 OK` `[ { "keyword": "Docker", "importance": "critical" } ]`
*   `GET /{analysis_id}/suggestions`
    *   **Description:** Get AI rewrite suggestions.
    *   **Response:** `200 OK` `[ { "section": "Experience", "original": "...", "suggested": "..." } ]`

---

## 5. Implementation Strategy
*   **Pydantic Models:** Use `schemas/` to strictly define Request/Response bodies.
*   **Status Codes:**
    *   `200`: Success
    *   `201`: Created
    *   `204`: Deleted
    *   `400`: Validation Error
    *   `401`: Unauthorized
    *   `404`: Not Found
    *   `422`: Unprocessable Entity (Pydantic validation fail)
