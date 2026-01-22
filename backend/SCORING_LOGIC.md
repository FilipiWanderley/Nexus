# Nexus Career AI - ATS Scoring Logic

## 1. Overview
The ATS Match Score (0–100) is a composite metric indicating how well a resume fits a specific job description. It is designed to mimic modern ATS algorithms (like Taleo, Greenhouse) combined with semantic understanding from LLMs.

**Target Output:** An integer score between 0 and 100.

---

## 2. The Formula

```
Total Score = (KwS * 0.40) + (SemS * 0.40) + (SenS * 0.20) - P
```

Where:
*   **KwS**: Keyword Match Score (0-100)
*   **SemS**: Semantic Similarity Score (0-100)
*   **SenS**: Seniority Fit Score (0-100)
*   **P**: Penalties (Absolute deduction)

---

## 3. Component Breakdown

### 3.1 Keyword Match Score (KwS) - Weight: 40%
Matches hard skills, tools, and certifications explicitly mentioned in the Job Description (JD).

*   **Extraction:** The AI extracts two lists from the JD:
    *   `Critical_Keywords` (Must-haves: e.g., "Python", "AWS", "React")
    *   `Bonus_Keywords` (Nice-to-haves: e.g., "Kubernetes", "Redis")
*   **Calculation:**
    ```python
    Critical_Hit_Rate = (Count(Found_Critical) / Count(Total_Critical)) * 100
    Bonus_Hit_Rate = (Count(Found_Bonus) / Count(Total_Bonus)) * 100
    
    KwS = (Critical_Hit_Rate * 0.70) + (Bonus_Hit_Rate * 0.30)
    ```

### 3.2 Semantic Similarity Score (SemS) - Weight: 40%
Measures the contextual alignment of experience. Does the resume *sound* like the job description?

*   **Method:**
    1.  Generate Text Embeddings (Vector) for the **Resume Experience Section**.
    2.  Generate Text Embeddings (Vector) for the **JD Responsibilities Section**.
    3.  Calculate **Cosine Similarity** (Result is 0.0 to 1.0).
*   **Calculation:**
    ```python
    SemS = Cosine_Similarity * 100
    ```
    *Note: If Cosine Similarity < 0.5, we floor it to 0 to penalize irrelevant resumes.*

### 3.3 Seniority Fit Score (SenS) - Weight: 20%
Evaluates if the candidate's experience level matches the role's requirements.

*   **Inputs:**
    *   `Required_YOE`: Extracted from JD (e.g., "5+ years").
    *   `Candidate_YOE`: Calculated from Resume dates.
    *   `Role_Type`: (e.g., Junior, Senior, Lead).
*   **Logic:**
    *   **Exact Match / Exceeds:** 100 points.
    *   **Within 1 Year (Under):** 80 points.
    *   **Within 2 Years (Under):** 50 points.
    *   **Significantly Under (>3 Years):** 0 points.
    *   *Weighting Adjustment:* For "Senior/Lead" roles, this component's internal weight increases implicitly because missing leadership keywords will also lower KwS.

### 3.4 Penalties (P)
Deductions for "Red Flags" that typically cause immediate rejection.

*   **Missing Critical Keyword:** -5 points per missing critical keyword (Max -20).
*   **Formatting Issues:** -5 points (e.g., unreadable text blocks, detected by parser).
*   **Length:** -5 points if word count < 300 (Too short) or > 2000 (Too long).

---

## 4. Implementation Strategy (Python)

We will use a specialized `ScoringService` class.

1.  **Parsing Phase:**
    *   Use `Gemini 2.0 Flash` to extract structured JSON from JD (Keywords, YOE, Seniority).
    *   Use `Gemini 2.0 Flash` to extract structured JSON from Resume (Skills, Experience List).

2.  **Vector Phase:**
    *   Use `google-generativeai` embeddings to get vectors for `SemS`.

3.  **Math Phase:**
    *   Apply the weighted formula.
    *   Return breakdown for UI visualization (e.g., "Your skills match, but your seniority is low").
