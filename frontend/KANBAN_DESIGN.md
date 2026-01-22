# Nexus Career AI - Kanban Job Tracker Design

## 1. Overview
A clean, drag-and-drop interface allowing users to visualize their job application pipeline. The goal is to reduce the cognitive load of job hunting.

## 2. Data Model (Recap)
Matches the `job_descriptions` table and `JobStatus` enum defined in the Backend Schema.

*   **Table:** `job_descriptions`
*   **Columns:**
    *   `id` (UUID)
    *   `title` (Text)
    *   `company` (Text)
    *   `status` (Enum: `saved`, `applied`, `interviewing`, `offer`, `rejected`)
    *   `updated_at` (Timestamp)

## 3. UI Columns Strategy

We map the database enum to user-friendly columns:

1.  **To Apply** (`saved`)
    *   *Color:* Slate (Neutral)
    *   *Icon:* Bookmark
2.  **Applied** (`applied`)
    *   *Color:* Blue
    *   *Icon:* PaperPlane
3.  **Interview** (`interviewing`)
    *   *Color:* Indigo
    *   *Icon:* VideoCamera
4.  **Feedback / Decision** (`offer` | `rejected`)
    *   *Color:* Mixed (Emerald for Offer, Rose for Rejected)
    *   *Icon:* CheckCircle / XCircle

## 4. Interaction Logic (Frontend)

We will use **dnd-kit** (lightweight, accessible React drag-and-drop library).

### 4.1 Optimistic Updates
1.  **User Event:** User drags card "Software Engineer @ Google" from *To Apply* to *Applied*.
2.  **Immediate UI Update:** The card snaps to the new column instantly.
3.  **API Call:** `PATCH /api/v1/jobs/{id}` with `{ "status": "applied" }`.
4.  **Rollback:** If the API fails (non-200), the card reverts to the original column and a Toast error appears.

### 4.2 Card Anatomy
*   **Header:** Job Title (Bold, truncated).
*   **Sub-header:** Company Name.
*   **Footer:** "Added 2 days ago" (Relative time).
*   **Action:** Click to open "Job Details Modal" (Edit, View Description, Delete).

## 5. Backend Persistence

*   **Endpoint:** `PATCH /api/v1/jobs/{job_id}`
*   **Logic:**
    1.  Validate `status` is a valid Enum value.
    2.  Check ownership (`user_id`).
    3.  Update record.
    4.  Return updated record.

## 6. Edge Cases
*   **Mobile:** On small screens, columns become a horizontal scroll or a tabbed view. Drag-and-drop is disabled in favor of a "Move to..." dropdown menu on the card.
*   **Empty States:** If a column is empty, show a ghost placeholder ("Drop here to move").
