# CopyCat Frontend — Phase 1: Project Inspection

This report documents the state of the frontend project as required by
**PHASE 1 — Project Inspection** in `FRONTEND_SPEC.md`.

No functional code was changed during this phase, per the spec:
"Do not make major changes during this phase."

---

## 1. Framework

| Item | Value |
| --- | --- |
| Framework | Next.js **16.3.3** (App Router, Turbopack build) |
| UI library | React **19.2.8** + React DOM **19.2.8** |
| Language | TypeScript 5 (`strict: true`) |
| Bootstrapped with | `create-next-app` (default scaffold, unmodified) |
| Package manager | npm (`package-lock.json` present) |
| Path alias | `@/*` → `./src/*` (defined in `tsconfig.json`) |

## 2. Routing

Routing uses the **Next.js App Router** (`src/app/` directory).

Current routes (verified via `npm run build`):

```text
/             Landing page  (default create-next-app scaffold — to be replaced)
/_not-found   Default 404
```

Target routes per spec §11 and how they map to App Router files:

```text
/                    src/app/page.tsx
/signin              src/app/signin/page.tsx
/signup              src/app/signup/page.tsx
/app                 src/app/app/page.tsx
/app/upload          src/app/app/upload/page.tsx
/app/analysis/:id    src/app/app/analysis/[id]/page.tsx
/app/history         src/app/app/history/page.tsx
```

Notes:

- `layout.tsx` uses typed routes (`LayoutProps<"/">`), Next 16 style.
- The app shell for `/app/*` can be a nested layout in Phase 5.

## 3. Styling

- **Tailwind CSS v4** via `@tailwindcss/postcss` (`postcss.config.mjs`).
- Tailwind v4 is configured **CSS-first** — there is no `tailwind.config.js`.
  Design tokens live in `@theme inline` blocks in `src/app/globals.css`.
- Fonts: `Geist` and `Geist_Mono` are loaded via `next/font/google` in
  `layout.tsx` and exposed as CSS variables `--font-geist-sans` /
  `--font-geist-mono`, mapped to `--font-sans` / `--font-mono` in
  `@theme inline`.
- Current scaffold state (to be addressed in Phase 2 — Design Foundation):
  - `globals.css` sets `body { font-family: Arial }`, which conflicts with
    the Geist variables wired in the layout.
  - Light/dark scheme is driven by `prefers-color-scheme`; the spec wants a
    fixed dark theme (`#080808` base) instead.
  - Spec color/accent tokens (#080808, #0D0D0D, #141414, #1A1A1A, #F5F5F5,
    #A1A1A1, #737373, rgba(255,255,255,0.10), #D94F4F, #7C6CF0) are **not**
    defined yet.

## 4. Existing Components

- **None.** There is no `components/` directory and no shared/reusable UI.
- `src/app/page.tsx` is the untouched create-next-app scaffold.
- `src/app/layout.tsx` is a lightly customized scaffold (fonts + flex body).
- `public/` contains only scaffold assets: `file.svg`, `globe.svg`,
  `next.svg`, `vercel.svg`, `window.svg`.
- Shared UI (buttons, section wrappers, nav) must be created in Phase 2/3
  under e.g. `src/components/`.

## 5. Dependencies

Runtime (`dependencies`):

| Package | Version | Notes |
| --- | --- | --- |
| next | 16.3.3 | Framework |
| react | 19.2.8 | UI |
| react-dom | 19.2.8 | UI |

Development (`devDependencies`):

| Package | Version | Notes |
| --- | --- | --- |
| tailwindcss | ^4 | Styling |
| @tailwindcss/postcss | ^4 | Tailwind PostCSS integration |
| typescript | ^5 | Type checking |
| eslint | ^9 | Linting |
| eslint-config-next | 16.3.3 | Next lint rules (core-web-vitals + TS) |
| @types/node, @types/react, @types/react-dom | ^19/^20 | Types |

Notable absences (fine for now — spec says avoid unnecessary dependencies):

- No animation library (spec wants subtle motion → CSS transitions are enough).
- No data-fetching/state library (use `fetch` + React built-ins).
- No component library (shadcn/radix, etc.) and no icon library.

NPM scripts: `dev`, `build`, `start`, `lint`.

## 6. Build Verification

`npm run build` was run in `frontend/` and **succeeds**:

```text
✓ Compiled successfully
✓ Finished TypeScript
Route (app)
┌ ○ /
└ ○ /_not-found
```


## 7. Backend Context (for later phases — inspected, not modified)

The repo contains a Python backend (`backend/`, managed with `uv`,
Python ≥ 3.13, FastAPI + google-genai + OpenCV). Relevant API surface in
`backend/src/backend/main.py`:

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/`, `/health` | Status |
| POST | `/upload-video` | Multipart `file` upload; must be `video/*`. Extracts frames every 1.0s (OpenCV), runs Gemini analysis synchronously, saves candidate rules |
| GET | `/rules` | Load validated rules |
| POST | `/rules/accept` | Accept a candidate rule |
| PUT / DELETE | `/rules/{rule_id}` | Edit / delete a rule |
| GET | `/test-gemini` | Gemini connectivity test |

`POST /upload-video` response shape (matches `LearningResult` in
`backend/src/backend/models/learning.py`):

```jsonc
{
  "message": "...",
  "video_id": "<uuid>",
  "original_filename": "...",
  "frames_extracted": 12,
  "analysis": {
    "goal": "string",
    "observations": [
      {
        "observable_fact": { "item": "...", "item_type": "...", "source_location": "...", "destination": "..." },
        "action": { "type": "..." },
        "inferred_decision": { "description": "...", "confidence": "..." }
      }
    ],
    "candidate_rules": [
      { "id": "...", "rule": "...", "confidence": "...", "evidence": ["..."], "requires_user_validation": true, "status": "pending" }
    ]
  }
}
```

Errors: `400` on invalid/unreadable video (ValueError), `503` when Gemini is
unavailable (ServerError).

Gaps / risks to resolve in Phases 6–8 (do **not** fix now):

1. **No CORS configuration** in the FastAPI app — a browser-based frontend on
   a different origin cannot call it yet. Either enable CORS on the backend or
   proxy through Next.js rewrites.
2. **No endpoints serve the uploaded video or extracted frames** back to the
   frontend (files sit in `backend/uploads/{id}.ext` and
   `backend/frames/{id}/frame_NNN_{ts}s.jpg`). Frame viewer / video viewer
   phases need this.
3. **No authentication system exists** in the backend — per spec §44 Phase 10,
   do not invent one.
4. No persistent analysis-history endpoint (only rules storage in JSON files
   under `backend/data/`).

Also noted: the backend has uncommitted local changes
(`main.py`, `models/learning.py`, `storage/rules.py`) unrelated to the
frontend — leave untouched.

## 8. Gap Summary → Feeds Next Phases

| Finding | Resolved in |
| --- | --- |
| Scaffold globals.css (light theme, Arial) vs spec dark tokens | Phase 2 — Design Foundation |
| No shared buttons/components | Phase 2 — Design Foundation |
| Landing page is default scaffold | Phase 3 — Landing Page Structure |
| No scroll/navbar motion | Phase 4 — Landing Page Polish |
| No `/app` shell/sidebar | Phase 5 — Application Layout |
| No upload UI; backend has no CORS + no file-serving endpoints | Phase 6 — Upload Experience (coordinate with backend) |
| No processing status UI; backend analysis is synchronous (single POST) | Phase 7 — Processing Experience |
| No analysis results UI | Phase 8 — Analysis Results |
| No history UI; no history endpoint | Phase 9 — History |
| No auth (frontend or backend) | Phase 10 — Authentication |

## 9. Phase 1 Conclusion

The project is a clean, unmodified Next.js 16 + React 19 + Tailwind v4
scaffold. It builds successfully. Architecture decisions for the next phases:

- Keep App Router; add routes as files under `src/app/` per the mapping in §2.
- Keep Tailwind v4 CSS-first token configuration; add spec tokens to
  `@theme` in `globals.css` in Phase 2.
- Build shared components with React + Tailwind only; add no new dependencies
  unless a later phase proves it necessary.
