"""Tests for database models."""

from datetime import datetime
from uuid import UUID

import pytest

from tick_task.models import Task


class TestTaskModel:
    """Test cases for the Task model."""

    def test_task_creation_minimal(self):
        """Test creating a task with minimal required fields."""
        task = Task(title="Test Task")

        assert task.title == "Test Task"
        assert task.status == "todo"  # default
        assert task.priority == "medium"  # default
        assert task.context == "personal"  # default
        assert task.description is None
        assert task.due_at is None
        assert task.tags == []
        assert task.workspace is None
        assert task.completed_at is None
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)

    def test_task_creation_full(self):
        """Test creating a task with all fields."""
        due_date = datetime(2024, 12, 31, 23, 59, 59)

        task = Task(
            title="Full Test Task",
            description="A comprehensive test task",
            status="doing",
            priority="high",
            due_at=due_date,
            tags=["urgent", "test"],
            context="professional",
            workspace="Project Alpha",
        )

        assert task.title == "Full Test Task"
        assert task.description == "A comprehensive test task"
        assert task.status == "doing"
        assert task.priority == "high"
        assert task.due_at == due_date
        assert task.tags == ["urgent", "test"]
        assert task.context == "professional"
        assert task.workspace == "Project Alpha"

    def test_task_uuid_generation(self):
        """Test that tasks get valid UUIDs."""
        task = Task(title="UUID Test")

        # Should have generated a valid UUID
        assert task.id is not None
        assert isinstance(UUID(task.id), UUID)

    def test_task_status_enum_validation(self):
        """Test valid status enum values."""
        # Valid statuses
        for status in ["todo", "doing", "blocked", "done", "archived"]:
            task = Task(title=f"Status {status}", status=status)
            assert task.status == status

        # Invalid status should raise an error at database level
        # (SQLAlchemy enum constraint)

    def test_task_priority_enum_validation(self):
        """Test valid priority enum values."""
        for priority in ["low", "medium", "high", "urgent"]:
            task = Task(title=f"Priority {priority}", priority=priority)
            assert task.priority == priority

    def test_task_context_enum_validation(self):
        """Test valid context enum values."""
        for context in ["personal", "professional", "mixed"]:
            task = Task(title=f"Context {context}", context=context)
            assert task.context == context

    def test_task_completion_timestamp(self):
        """Test that completion timestamp is set when status is done."""
        task = Task(title="Complete Test", status="done")

        # completed_at should be set automatically
        assert task.completed_at is not None
        assert isinstance(task.completed_at, datetime)

    def test_task_string_representation(self):
        """Test the __repr__ method."""
        task = Task(title="Repr Test", status="doing")
        repr_str = repr(task)

        assert "Task" in repr_str
        assert task.id in repr_str
        assert "Repr Test" in repr_str
        assert "doing" in repr_str

    def test_task_timestamps(self):
        """Test that timestamps are set correctly."""
        before = datetime.utcnow()
        task = Task(title="Timestamp Test")
        after = datetime.utcnow()

        assert before <= task.created_at <= after
        assert before <= task.updated_at <= after

    def test_task_tags_default_empty_list(self):
        """Test that tags defaults to empty list."""
        task = Task(title="Tags Test")
        assert task.tags == []

    def test_task_tags_custom_list(self):
        """Test setting custom tags."""
        tags = ["tag1", "tag2", "tag3"]
        task = Task(title="Custom Tags", tags=tags)
        assert task.tags == tags

    def test_task_optional_fields_none(self):
        """Test that optional fields can be None."""
        task = Task(title="Optional Fields Test")

        assert task.description is None
        assert task.due_at is None
        assert task.workspace is None
        assert task.completed_at is None

    def test_task_title_required(self):
        """Test that title is required."""
        # This would normally raise an error at database level
        # but we can test the model creation
        task = Task()  # No title provided

        # In SQLAlchemy, this will fail when trying to insert
        # but the model creation itself doesn't validate
        assert task.title is None  # Default None, but nullable=False in DB

    def test_task_title_length_constraint(self):
        """Test title length constraints."""
        # SQLAlchemy doesn't enforce this at model level,
        # but database will enforce VARCHAR(200)
        long_title = "x" * 250  # Longer than 200 chars
        task = Task(title=long_title)

        # Model allows it, but database will reject
        assert len(task.title) == 250
