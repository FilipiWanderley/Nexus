# Nexus Career AI - Keyword Gap Analysis System

## 1. Objective
To systematically identify the discrepancy between a candidate's resume and a job description's (JD) technical requirements, classifying these gaps by importance to guide the user's optimization efforts.

## 2. System Workflow

```mermaid
graph LR
    JD[Job Description] -->|Gemini 2.0| Extractor[Skill Extractor]
    Resume[Resume Text] -->|Gemini 2.0| Extractor
    
    Extractor -->|Required Skills (Weighted)| Comparator
    Extractor -->|Candidate Skills (Found)| Comparator
    
    Comparator -->|Logic Engine| Gaps[Gap List]
    Gaps -->|Format| JSON[Structured Response]
```

## 3. Skill Extraction Logic (AI-Driven)

We utilize **Gemini 2.0 Flash** with a strict schema to extract skills from the JD.

### 3.1 Importance Classification Rules
The AI assigns an `importance` level based on semantic context:
*   **CRITICAL**:
    *   Phrases: "Must have", "Required", "Core", "Deep understanding of".
    *   Frequency: Appears > 3 times in the JD.
    *   Placement: Listed in "Minimum Qualifications".
*   **HIGH**:
    *   Phrases: "Proficiency in", "Strong knowledge of".
    *   Placement: Listed in the main body or first 3 bullets of responsibilities.
*   **MEDIUM**:
    *   Phrases: "Experience with", "Familiarity with", "Preferred", "Plus".
    *   Placement: "Preferred Qualifications" section.
*   **LOW**:
    *   Mentions of generic tools or "nice to have" fringe technologies.

### 3.2 Detection & Normalization
*   **Normalization**: "React.js", "ReactJS", "React" -> `React`.
*   **Categorization**: Skills are grouped (e.g., Languages, Frameworks, Cloud, Databases) to help the UI organize the gaps.

## 4. Gap Detection Logic

### 4.1 Comparison States
For each **Required Skill** identified in the JD, we check the **Resume Content**:

1.  **MISSING**:
    *   The term (or its synonyms) is completely absent from the resume.
    *   *Action:* Flag as a gap.
2.  **PARTIAL (Weak)**:
    *   The term is present, but context implies low proficiency compared to requirement.
    *   *Example:* JD asks for "Expert Python" (Critical), Resume says "Familiar with Python" or lists it only in a "Interests" section.
    *   *Action:* Flag as a gap with specific advice (e.g., "Strengthen this skill").
3.  **PRESENT**:
    *   The term matches well.
    *   *Action:* No gap.

## 5. Data Structures

### 5.1 AI Extraction Schema (Internal)
```python
class ExtractedSkill(BaseModel):
    name: str
    category: str  # "Language", "Tool", "Soft Skill"
    importance: Literal["critical", "high", "medium", "low"]
    context_in_jd: str  # Snippet where it was found
```

### 5.2 API Response (Frontend Consumption)
Matches the `KeywordGapResponse` schema defined earlier.

```json
[
  {
    "id": "uuid",
    "keyword": "Kubernetes",
    "category": "DevOps",
    "importance": "critical",
    "status": "missing",
    "advice": "Add a project or experience highlighting container orchestration."
  },
  {
    "id": "uuid",
    "keyword": "GraphQL",
    "category": "API",
    "importance": "medium",
    "status": "partial",
    "advice": "Move GraphQL from 'Other Skills' to a specific work experience bullet."
  }
]
```

## 6. Implementation Strategy

1.  **Prompt Engineering**: Create a robust system prompt for Gemini that enforces the extraction schema.
2.  **Fuzzy Matching**: Use `thefuzz` (Python library) as a fallback layer to catch slight misspellings (e.g., "Kubernetes" vs "K8s") before declaring a skill "Missing", if the AI misses the synonym connection.
3.  **Caching**: Cache the extraction results of the JD so we don't re-process the same JD multiple times for the same user session.
