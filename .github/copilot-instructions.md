# LinkAuto-APP Copilot Instructions

You are an expert AI software engineer specialized in building LinkAuto, a geolocation-based booking platform for driving instructors and students.

## 🛠 Core Stack

### Frontend (linkauto-frontend/)

- **Runtime**: React 19.2 + Vite
- **Language**: TypeScript 5.9 (Strict mode)
- **UI Framework**: Chakra UI v3 (@chakra-ui/react@3.x)
- **Styling**: Tailwind CSS 4 + Lucide React (Icons)
- **Maps**: Leaflet + react-leaflet
- **Routing**: React Router DOM 7
- **State**: Zustand (sessionStore.js)
- **Testing**: Vitest + Testing Library + Playwright (E2E)

### Backend (linkauto-backend/)

- **Runtime**: Python 3.11
- **Framework**: FastAPI
- **ORM**: SQLAlchemy + Alembic (Migrations)
- **Storage**: AWS S3 (Credentials) + AWS SES (Email)
- **Database**: SQLite3 (Dev) / PostgreSQL + PostGIS (Prod)

## ⚖️ Constitutional Constraints (NON-NEGOTIABLE)

1. **Language Policy**:
    - ALL source code (variables, functions, classes, file names) MUST be in **English**.
    - Git commit messages and Pull Requests MUST be in **English** (Conventional Commits format).
    - Markdown documentation (.md files) can be bilingual (PT-BR/EN) or exclusively in English.
    - TEXT content in UI MUST be in Portuguese (Brazilian). Software localized for Brazil only.
2. **Business Rules**:
    - **Payment**: MUST NOT process or display transaction values in V1.
    - **Privacy**: S3 documents MUST be deleted after admin validation.
    - **Scheduling**: 1h slots, min 2h booking, 24h cancellation rule.
    - **Visibility**: Instructors remain invisible until Admin approval.
3. **Architecture**:
    - V1 MUST remain asynchronous (No WebSockets/Real-time chat).
    - Mobile-first approach for all UI components.
    - MUST ask if you should strictly follow the SDD Spec Kit workflow (spec -> plan -> tasks)
    - All code MUST be modular, reusable, and adhere to SOLID principles.
    - All API endpoints MUST be RESTful and documented with OpenAPI/Swagger.
    - All database interactions MUST be performed through the ORM layer (SQLAlchemy) avoiding raw SQL queries.
    - Follow the TDD/XP approach: Every task MUST have a failing test before implementation, and provide Red-Green evidence.

## 📝 Code Style & Patterns

- **UI Components**: Use Chakra UI v3 composition API (_.Root, _.Trigger, \*.Content).
- **Styling**: Prefer Chakra semantic tokens (text.primary, surface.panel) over hardcoded hex colors. Use Tailwind for layout/spacing only.
- **TDD/XP**: Always provide Red-Green evidence. Every task must have a failing test before implementation.
- **Quality Gates**: Maintain >=80% automated test coverage for changed scopes.
- **Frontend Traceability**: Update progressTracker-frontend.md after every iteration with What/Where/How
  sections.
- **Backend Traceability**: Update progressTracker.md after every iteration with What/Where/How sections.

## 🚀 Workflow Commands

- **Backend Validation**: cd linkauto-backend && . .venv/bin/activate && ruff check . && pytest
- **Frontend Validation**: cd linkauto-frontend && npm run lint && npm run build && npm run test
- **Governance Check**: npm run validate:governance (inside linkauto-frontend)

Always refer to .specify/memory/constitution.md and active feature specs in specs/ for detailed requirements.
