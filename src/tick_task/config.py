"""Application configuration."""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Server settings
    host: str = Field("127.0.0.1", description="Server host")
    port: int = Field(7000, description="Server port", ge=1024, le=65535)
    debug: bool = Field(False, description="Debug mode")

    # Database settings
    database_url: str = Field(
        "sqlite+aiosqlite:///./tick-task.db", description="Database connection URL"
    )

    # Application settings
    data_dir: Path = Field(
        Path.home() / ".tick-task", description="Data directory path"
    )

    # LAN mode settings (disabled by default)
    lan_mode: bool = Field(False, description="Enable LAN mode")
    lan_token: Optional[str] = Field(None, description="LAN access token")

    class Config:
        """Pydantic configuration."""

        env_prefix = "TICK_TASK_"
        case_sensitive = False

    @property
    def database_path(self) -> Path:
        """Get the database file path."""
        if self.database_url.startswith("sqlite"):
            # Extract path from sqlite:///./path or sqlite+aiosqlite:///./path
            url_parts = self.database_url.split("://")
            if len(url_parts) == 2:
                path_part = url_parts[1]
                if path_part.startswith("./"):
                    return Path(path_part[2:])
                elif path_part.startswith("/"):
                    return Path(path_part)
        return self.data_dir / "tick-task.db"

    def ensure_data_dir(self) -> None:
        """Ensure the data directory exists."""
        self.data_dir.mkdir(parents=True, exist_ok=True)


# Create global settings instance
settings = Settings()
settings.ensure_data_dir()
