# Nexus Career AI - Row Level Security (RLS) Design

## Security Philosophy

We adopt a **"Trust the Backend, Verify the User"** model.

1.  **User Data (`profiles`, `resumes`, `job_descriptions`)**: Users have full CRUD access to their own data. They own these assets.
2.  **AI Data (`analyses`, `keyword_gaps`, `rewrite_suggestions`)**: Users have **Read-Only** access.
    *   *Why?* To prevent users from manually tampering with match scores or inserting fake "perfect" analyses.
    *   *Creation:* The Python Backend uses the **Service Role Key** (admin privileges) to write these records after processing.
    *   *Deletion:* Users can DELETE an analysis (which cascades), but they cannot UPDATE the score.

## Performance Considerations

*   **Foreign Key Indexing**: RLS policies for child tables (`keyword_gaps`) rely on joins to parent tables (`analyses`). We must index `analysis_id` to ensure these permission checks are fast.

---

## Detailed Policy Logic

### 1. Profiles
*   `SELECT`: `auth.uid() = id` (User sees own profile).
*   `UPDATE`: `auth.uid() = id` (User updates own profile).
*   `INSERT`: Disabled for users. Handled by System Trigger on Auth Signup.

### 2. Resumes & Job Descriptions
*   `ALL` (Select, Insert, Update, Delete): `auth.uid() = user_id`.

### 3. Analyses
*   `SELECT`: `auth.uid() = user_id`.
*   `DELETE`: `auth.uid() = user_id`.
*   `INSERT/UPDATE`: **Denied** for public role (User). Allowed only for Service Role.

### 4. Keyword Gaps & Rewrite Suggestions
*   `SELECT`: Check if the parent `analysis` belongs to the user:
    ```sql
    EXISTS (SELECT 1 FROM analyses WHERE id = analysis_id AND user_id = auth.uid())
    ```
*   `INSERT/UPDATE/DELETE`: **Denied** for public role.
