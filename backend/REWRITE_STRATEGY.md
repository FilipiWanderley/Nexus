# Nexus Career AI - Resume Rewrite Strategy

## 1. Core Philosophy: "Polished Truth"
The AI must never invent facts (hallucinate). Instead, it acts as a **professional editor**, restructuring the user's existing content to be more impactful, quantifiable, and ATS-friendly.

## 2. Rewrite Rules (The "XYZ" Formula)

We adopt Google's "Accomplished [X] as measured by [Y], by doing [Z]" framework, adapted for different seniority levels.

### Rule 1: Action Verb First
*   **Bad:** "Responsible for managing the team."
*   **Good:** "Led a cross-functional team..."
*   **Constraint:** Must use strong verbs from our curated `Action_Verbs_DB` (e.g., *Architected, Optimized, Spearheaded*).

### Rule 2: Quantify Results (The "[Y] Constraint")
*   **Logic:** If the user provides a number ("increased sales by 10%"), preserve and highlight it.
*   **AI Instruction:** "If no number is present, ask the user a clarifying question OR rewrite to emphasize the *scale* or *impact* qualitatively (e.g., 'resulting in improved system stability')."

### Rule 3: ATS Optimization
*   **Logic:** Integrate keywords from the specific Job Description (JD) naturally.
*   **Constraint:** Do not stuff keywords. Use them as the *object* of the action verb.
    *   *Original:* "Used Python for backend."
    *   *JD Keyword:* "FastAPI".
    *   *Rewrite:* "Developed high-performance backend microservices using **Python** and **FastAPI**..."

---

## 3. Tone Adjustment by Seniority

The AI modifies its output style based on the user's target role.

### Level 1: Junior / Entry (0-3 Years)
*   **Focus:** Learning, Execution, Participation.
*   **Tone:** Eager, Technical, Task-Oriented.
*   **Verbs:** *Built, Assisted, Collaborated, Implemented.*
*   **Example:**
    *   *Original:* "I helped fix bugs in the app."
    *   *Rewrite:* "Collaborated with senior developers to **debug and resolve** critical issues in the React Native application, improving crash-free rate."

### Level 2: Mid-Level (3-7 Years)
*   **Focus:** Ownership, Efficiency, Mentorship.
*   **Tone:** Competent, Independent, Results-Driven.
*   **Verbs:** *Engineered, Deployed, Refactored, Mentored.*
*   **Example:**
    *   *Original:* "I made the API faster."
    *   *Rewrite:* "**Optimized** REST API endpoints by implementing Redis caching, reducing average response time by **40%**."

### Level 3: Senior / Lead (7+ Years)
*   **Focus:** Strategy, Architecture, Business Impact.
*   **Tone:** Authoritative, Visionary, Strategic.
*   **Verbs:** *Architected, Spearheaded, Directed, Scaled.*
*   **Example:**
    *   *Original:* "We moved to the cloud."
    *   *Rewrite:* "**Spearheaded** the digital transformation strategy, migrating legacy on-premise infrastructure to **AWS**, resulting in a **$50k annual cost reduction**."

---

## 4. Anti-Hallucination Guardrails

To prevent the AI from making things up, we use a **"Conservative Rewriting"** system prompt:

1.  **Fact-Check:** "Does the rewritten sentence contain any specific entity (tool, number, outcome) not present in the original text? If yes, REMOVE IT."
2.  **Placeholder Strategy:** If a metric is needed but missing, use a placeholder.
    *   *Rewrite:* "Reduced build times by **[percentage]%** through CI/CD pipeline optimization."
    *   *UI Action:* The frontend highlights `[percentage]%` and prompts the user to fill it in.

---

## 5. Technical Implementation (Gemini Prompt)

```text
You are an expert Resume Editor. Rewrite the following bullet point for a [SENIORITY] Software Engineer.

Input: "{original_text}"
Target Keywords: {keywords}

Rules:
1. Start with a strong action verb.
2. Incorporate target keywords naturally.
3. PRESERVE ALL FACTS. Do not invent numbers or tools.
4. If the input is vague, make it sound professional but do not overclaim.
5. Output format: JSON { "rewrite": "...", "reasoning": "..." }
```
