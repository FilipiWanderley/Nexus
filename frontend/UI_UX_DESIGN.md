# Nexus Career AI - UI/UX Architecture

## 1. Design Philosophy
**"Clarity over Clutter."**
The interface mimics high-end developer tools (like Vercel or Linear)—minimalist, monochromatic with purposeful accent colors, and highly responsive.

*   **Font:** Inter (Clean, sans-serif).
*   **Colors:** Slate (Backgrounds), Indigo (Primary Actions), Emerald (Success/High Score), Rose (Errors/Gaps).
*   **Accessibility:** WCAG 2.1 AA compliant (high contrast, keyboard navigable).

---

## 2. App Router Structure (`src/app`)

```
src/app/
├── (auth)/                 # Authentication Group (No sidebar)
│   ├── login/page.tsx
│   ├── signup/page.tsx
│   └── layout.tsx          # Centered card layout
├── (dashboard)/            # Protected App Area (Sidebar + Header)
│   ├── layout.tsx          # Shell: AuthGuard + Sidebar + Navbar
│   ├── page.tsx            # Dashboard Home (Stats overview)
│   ├── resumes/
│   │   ├── page.tsx        # List of uploaded resumes
│   │   └── [id]/page.tsx   # Resume Detail View
│   ├── jobs/               # Kanban Board
│   │   └── page.tsx
│   └── analysis/
│       └── [id]/page.tsx   # The Core Optimization View
├── api/                    # Next.js API Routes (if needed for proxy)
├── globals.css             # Tailwind imports
└── layout.tsx              # Root Layout (Providers)
```

---

## 3. Component Strategy (`src/components`)

We follow the **Atomic Design** principle, adapted for React.

### 3.1 `ui/` (Atoms/Molecules)
Reusable, dumb components based on **shadcn/ui** (headless UI + Tailwind).
*   `Button`, `Input`, `Card`, `Badge`, `Progress`, `Skeleton`.
*   `Toast` (for notifications).

### 3.2 `features/` (Organisms)
Domain-specific logic blocks.
*   **`resume/`**: `ResumeUploader`, `ResumeList`, `ResumePreview`.
*   **`job/`**: `JobKanbanBoard`, `JobCard`, `AddJobModal`.
*   **`analysis/`**:
    *   `ScoreGauge`: Visual meter for 0-100 score.
    *   `GapList`: Interactive list of missing keywords.
    *   `RewriteCard`: Before/After comparison with "Apply" button.

### 3.3 `layout/` (Templates)
*   `Sidebar`: Navigation.
*   `Header`: User profile dropdown, Breadcrumbs.
*   `Shell`: Wrapper for protected pages.

---

## 4. State Management Approach

1.  **Server State (React Query / TanStack Query):**
    *   Used for *all* async data (Resumes, Jobs, Analysis results).
    *   Handles caching, loading states (`isLoading`), and re-fetching.
2.  **Global UI State (Zustand):**
    *   Minimal usage. Mostly for UI preferences (Sidebar toggle, Dark mode) or complex multi-step form state (Wizard).
3.  **Local State (React `useState`):**
    *   Form inputs, modal visibility, optimistic UI updates.

---

## 5. UX Patterns

### 5.1 Loading States
*   **Skeletons:** Never show a blank screen. Use `Skeleton` components that mimic the shape of the content (e.g., a list of resume cards) while data fetches.
*   **Streaming:** For AI analysis, use streaming text or step-by-step progress indicators ("Parsing PDF...", "Analyzing Keywords...", "Generating Suggestions...") to keep the user engaged during the 5-10s wait.

### 5.2 Error Handling
*   **Toast Notifications:** For transient errors ("Failed to save").
*   **Error Boundaries:** Wrap major route segments. If the "Analysis" view crashes, the "Sidebar" remains functional.
*   **Empty States:** "No resumes yet? Upload your first one!" (with a big CTA button).

### 5.3 Optimistic Updates
*   When moving a job card in Kanban, update the UI *immediately*, then sync with the server. Revert if it fails.

---

## 6. Accessibility (a11y)
*   **Focus Management:** Ensure modals trap focus.
*   **Semantic HTML:** Use `<main>`, `<nav>`, `<aside>`, `<h1>-<h6>`.
*   **ARIA Labels:** For icon-only buttons (e.g., "Delete Resume").
*   **Keyboard Nav:** Full support for Kanban board drag-and-drop via keyboard.
