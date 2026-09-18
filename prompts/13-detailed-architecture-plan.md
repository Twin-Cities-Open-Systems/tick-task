# Agent Prompt 13 — Detailed Architecture Plan

## Objective
Create a complete implementation-ready architecture specification incorporating user requirements.

## Technology Stack Decisions
- **Backend Framework**: Python FastAPI (async, auto-docs, minimal deps)
- **ORM/Persistence**: SQLAlchemy + SQLite (local-first, crash-safe, proven)
- **Frontend Framework**: React 18 + TypeScript (accessibility, component ecosystem, type safety)
- **Styling**: Tailwind CSS (utility-first, responsive, small bundle)
- **Build Tools**: Vite (fast HMR) + setuptools (Python packaging)
- **Testing**: pytest + Playwright (comprehensive coverage)
- **Auth**: Authlib for OAuth (Google), fallback to simple token auth

## Architecture Layers
### Domain Layer
- Task entity with validation (Pydantic models)
- Business logic for task operations
- Query/filtering logic

### Persistence Layer
- SQLAlchemy ORM with SQLite backend
- Migration system (Alembic)
- Crash-safe transactions
- Export functionality (JSON/CSV)

### API Layer
- FastAPI with automatic OpenAPI docs
- Request/response validation
- Error handling with proper HTTP status codes
- CORS configuration for local development

### UI Layer
- React components with TypeScript
- State management (React Query + Context)
- Responsive design with Tailwind
- Accessibility (WCAG 2.1 AA compliance)

## Security Architecture
- Default: localhost-only (127.0.0.1)
- Optional LAN mode with token authentication
- OAuth integration for Google (if feasible)
- Admin-only fallback mode
- Input validation and sanitization

## Data Flow
1. UI makes requests to local API
2. API validates requests and calls domain logic
3. Domain logic orchestrates persistence operations
4. SQLite handles data durability
5. Responses flow back through layers

## Deployment Architecture
- Single binary/package for easy local installation
- Configuration via environment variables or config file
- Automatic database initialization
- Graceful shutdown handling

## Output
- Update docs/ARCHITECTURE.md with complete implementation details
- Add technology decisions to docs/DECISIONS.md
- Create docs/DEPENDENCIES.md with justification for each third-party library <!-- hee-check:refs-ok the prompt asks for this file to be written -->
- Ensure all choices support local-first, minimal-dependency principles
