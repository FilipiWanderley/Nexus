# Nexus Career AI - Design System

## 1. Typography (Inter)
We use **Inter** for its excellent readability and neutral, professional tone.

*   **H1 (Page Title):** `text-3xl font-semibold tracking-tight` (30px)
*   **H2 (Section):** `text-2xl font-medium tracking-tight` (24px)
*   **H3 (Card Title):** `text-lg font-medium` (18px)
*   **Body:** `text-sm text-slate-600 leading-relaxed` (14px) - *Default text size for density.*
*   **Small:** `text-xs text-slate-500` (12px) - *Metadata, timestamps.*

## 2. Color Palette (Tailwind Mapping)

### Neutrals (Structure)
*   **Surface:** `bg-white` (Main), `bg-slate-50` (App Background)
*   **Borders:** `border-slate-200` (Subtle), `border-slate-300` (Hover)
*   **Text:** `text-slate-900` (Primary), `text-slate-500` (Secondary/Muted)

### Primary (Action - Indigo)
*   **Brand:** `bg-indigo-600` (Main), `bg-indigo-700` (Hover)
*   **Subtle:** `bg-indigo-50 text-indigo-700` (Badges, Selected states)

### Functional (Feedback)
*   **Success (High Score):** `text-emerald-600`, `bg-emerald-50`
*   **Warning (Partial Gap):** `text-amber-600`, `bg-amber-50`
*   **Error (Missing/Critical):** `text-rose-600`, `bg-rose-50`

## 3. Spacing Scale (4px grid)
*   **Compact:** `p-2` (8px), `gap-2`
*   **Standard:** `p-4` (16px), `gap-4`
*   **Section:** `p-6` (24px), `gap-6`
*   **Layout:** `p-8` (32px)

## 4. Components

### 4.1 Buttons
*   **Primary:** `bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm rounded-md px-4 py-2 font-medium transition-all`
*   **Secondary:** `bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 shadow-sm rounded-md px-4 py-2 font-medium`
*   **Ghost:** `text-slate-600 hover:bg-slate-100 rounded-md px-3 py-2`

### 4.2 Cards
*   **Standard:** `bg-white border border-slate-200 rounded-lg shadow-sm hover:shadow-md transition-shadow`
*   **Interactable:** `cursor-pointer hover:border-indigo-300`

### 4.3 Inputs
*   **Default:** `border-slate-200 rounded-md shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500`

## 5. Feedback States
*   **Loading:** Skeleton loaders (`animate-pulse bg-slate-100 rounded`) matching the content shape.
*   **Empty:** Centered illustration (SVG) with a Title (`text-slate-900`), Description (`text-slate-500`), and a Primary Action Button.
