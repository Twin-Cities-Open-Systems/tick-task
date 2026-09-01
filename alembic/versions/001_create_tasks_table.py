"""Create tasks table

Revision ID: 001
Revises:
Create Date: 2026-01-21 13:31:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create tasks table
    op.create_table(
        "tasks",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("todo", "doing", "blocked", "done", "archived", name="task_status"),
            nullable=False,
        ),
        sa.Column(
            "priority",
            sa.Enum("low", "medium", "high", "urgent", name="task_priority"),
            nullable=False,
        ),
        sa.Column("due_at", sa.DateTime(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column(
            "context",
            sa.Enum("personal", "professional", "mixed", name="task_context"),
            nullable=False,
        ),
        sa.Column("workspace", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for better query performance
    op.create_index("ix_tasks_status", "tasks", ["status"])
    op.create_index("ix_tasks_context", "tasks", ["context"])
    op.create_index("ix_tasks_priority", "tasks", ["priority"])
    op.create_index("ix_tasks_due_at", "tasks", ["due_at"])
    op.create_index("ix_tasks_updated_at", "tasks", ["updated_at"])
    op.create_index("ix_tasks_created_at", "tasks", ["created_at"])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index("ix_tasks_created_at", table_name="tasks")
    op.drop_index("ix_tasks_updated_at", table_name="tasks")
    op.drop_index("ix_tasks_due_at", table_name="tasks")
    op.drop_index("ix_tasks_priority", table_name="tasks")
    op.drop_index("ix_tasks_context", table_name="tasks")
    op.drop_index("ix_tasks_status", table_name="tasks")

    # Drop table
    op.drop_table("tasks")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS task_context")
    op.execute("DROP TYPE IF EXISTS task_priority")
    op.execute("DROP TYPE IF EXISTS task_status")
