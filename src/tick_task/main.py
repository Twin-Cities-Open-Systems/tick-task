"""Main FastAPI application."""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from tick_task.api import router as api_router
from tick_task.config import settings
from tick_task.database import create_tables


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title="FIN-tasks",
        description="Local-first task management application",
        version="0.5.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],  # Vite dev server
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Root route - redirect to API docs
    @app.get("/", include_in_schema=False)
    async def root():
        """Redirect root to API documentation."""
        return RedirectResponse(url="/docs")

    # Include API routes
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_application()


def main():
    """Run the application with uvicorn."""
    uvicorn.run(
        "tick_task.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info",
    )


if __name__ == "__main__":
    main()
