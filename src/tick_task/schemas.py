"""Pydantic schemas for API validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskBase(BaseModel):
    """Base task schema with common fields."""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(
        None, max_length=2000, description="Task description"
    )
    status: str = Field(
        "todo",
        description="Task status",
        pattern=r"^(todo|doing|blocked|done|archived)$",
    )
    priority: str = Field(
        "medium", description="Task priority", pattern=r"^(low|medium|high|urgent)$"
    )
    due_at: Optional[datetime] = Field(
        None, description="Due date and time in ISO format"
    )
    tags: list[str] = Field(default_factory=list, description="List of tags")
    context: str = Field(
        "personal",
        description="Task context",
        pattern=r"^(personal|professional|mixed)$",
    )
    workspace: Optional[str] = Field(None, max_length=100, description="Workspace name")

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tag(cls, v):
        """Validate individual tag constraints."""
        if isinstance(v, list):
            validated_tags = []
            for tag in v:
                if len(tag) > 50:
                    raise ValueError("Tag must be 50 characters or less")
                if not tag.strip():
                    raise ValueError("Tag cannot be empty or whitespace-only")
                validated_tags.append(tag.strip().lower())
            return validated_tags
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        """Validate title is not empty after stripping."""
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace-only")
        return v.strip()

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
        }
    )

    def model_dump_json(self, **kwargs):
        """Custom JSON serialization that handles datetime fields properly."""
        # Set default datetime format to include 'Z' for UTC
        kwargs.setdefault("serialize_as_any", True)
        return super().model_dump_json(**kwargs)


class TaskCreate(TaskBase):
    """Schema for creating a new task."""

    pass


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[str] = Field(None, pattern=r"^(todo|doing|blocked|done|archived)$")
    priority: Optional[str] = Field(None, pattern=r"^(low|medium|high|urgent)$")
    due_at: Optional[datetime] = None
    tags: Optional[list[str]] = None
    context: Optional[str] = Field(None, pattern=r"^(personal|professional|mixed)$")
    workspace: Optional[str] = Field(None, max_length=100)

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tag(cls, v):
        """Validate individual tag constraints."""
        if isinstance(v, list) and v is not None:
            for tag in v:
                if len(tag) > 50:
                    raise ValueError("Tag must be 50 characters or less")
                if not tag.strip():
                    raise ValueError("Tag cannot be empty or whitespace-only")
                tag = tag.strip().lower()
            return v
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        """Validate title is not empty after stripping."""
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty or whitespace-only")
        return v.strip() if v is not None else v

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
        }
    )


class Task(TaskBase):
    """Full task schema for responses."""

    id: str = Field(..., description="Task UUID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
        },
    )


class TaskList(BaseModel):
    """Schema for task list responses with pagination."""

    tasks: list[Task] = Field(..., description="List of tasks")
    pagination: dict = Field(..., description="Pagination metadata")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
        }
    )


class HealthResponse(BaseModel):
    """Schema for health check responses."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    database: str = Field(..., description="Database status")
    timestamp: datetime = Field(..., description="Response timestamp")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
        }
    )


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    error: dict = Field(..., description="Error details")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
        }
    )
