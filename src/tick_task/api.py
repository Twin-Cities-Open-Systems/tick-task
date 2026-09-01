"""API routes for FIN-tasks."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from tick_task.database import get_db
from tick_task.models import Task
from tick_task.schemas import ErrorResponse, HealthResponse
from tick_task.schemas import Task as TaskSchema
from tick_task.schemas import TaskCreate, TaskList, TaskUpdate

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns the health status of the API service",
)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Check service health and database connectivity."""
    try:
        # Test database connection
        from sqlalchemy import text

        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return HealthResponse(
        status="healthy",
        version="0.4.0",
        database=db_status,
        timestamp=datetime.utcnow(),
    )


@router.post(
    "/tasks",
    response_model=TaskSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create task",
    description="Create a new task with the provided data",
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
) -> TaskSchema:
    """Create a new task."""
    # Create task instance
    task = Task(
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        due_at=task_data.due_at,
        tags=task_data.tags,
        context=task_data.context,
        workspace=task_data.workspace,
    )

    # Set completion timestamp if status is done
    if task.status == "done":
        task.completed_at = datetime.utcnow()

    # Add to database
    db.add(task)
    await db.commit()
    await db.refresh(task)

    return TaskSchema.from_orm(task)


@router.get(
    "/tasks/{task_id}",
    response_model=TaskSchema,
    summary="Get task",
    description="Retrieve a specific task by ID",
    responses={
        404: {"model": ErrorResponse, "description": "Task not found"},
        400: {"model": ErrorResponse, "description": "Invalid UUID format"},
    },
)
async def get_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> TaskSchema:
    """Get a specific task by ID."""
    task = await db.get(Task, str(task_id))
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return TaskSchema.from_orm(task)


@router.put(
    "/tasks/{task_id}",
    response_model=TaskSchema,
    summary="Update task",
    description="Update an existing task with the provided data",
    responses={
        404: {"model": ErrorResponse, "description": "Task not found"},
        409: {"model": ErrorResponse, "description": "Cannot update archived task"},
        400: {"model": ErrorResponse, "description": "Validation error"},
    },
)
async def update_task(
    task_id: UUID,
    task_update: TaskUpdate,
    db: AsyncSession = Depends(get_db),
) -> TaskSchema:
    """Update an existing task."""
    task = await db.get(Task, str(task_id))
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Check if task is archived
    if task.status == "archived":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot update archived task",
        )

    # Apply updates
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    # Update completion timestamp based on status
    if task.status == "done" and not task.completed_at:
        task.completed_at = datetime.utcnow()
    elif task.status != "done":
        task.completed_at = None

    # Update timestamp
    task.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(task)

    return TaskSchema.from_orm(task)


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete task",
    description="Archive a task (soft delete)",
    responses={
        404: {"model": ErrorResponse, "description": "Task not found"},
        409: {"model": ErrorResponse, "description": "Task already archived"},
    },
)
async def delete_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> TaskSchema:
    """Soft delete (archive) a task."""
    task = await db.get(Task, str(task_id))
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task.status == "archived":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task already archived",
        )

    # Archive the task
    task.status = "archived"
    task.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(task)

    return TaskSchema.from_orm(task)


@router.get(
    "/tasks",
    response_model=TaskList,
    summary="List tasks",
    description=(
        "Retrieve a list of tasks with optional filtering, sorting, "
        "and pagination"
    ),
)
async def list_tasks(
    # Filtering parameters
    status: Optional[list[str]] = Query(
        None, description="Filter by status (can specify multiple)"
    ),
    context: Optional[str] = Query(None, description="Filter by context"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    priority: Optional[str] = Query(None, description="Minimum priority level"),
    due_before: Optional[datetime] = Query(None, description="Tasks due before date"),
    due_after: Optional[datetime] = Query(None, description="Tasks due after date"),
    updated_since: Optional[datetime] = Query(
        None, description="Tasks updated since date"
    ),
    # Sorting parameters
    sort: str = Query("updated_at", description="Sort field"),
    order: str = Query("desc", description="Sort order (asc/desc)"),
    # Pagination parameters
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    db: AsyncSession = Depends(get_db),
) -> TaskList:
    """List tasks with filtering, sorting, and pagination."""
    # Build query
    query = select(Task)

    # Apply filters
    if status:
        query = query.where(Task.status.in_(status))

    if context:
        query = query.where(Task.context == context)

    # TODO: Implement proper JSON array filtering for tags
    # For now, skip tag filtering to avoid SQL errors
    # if tags:
    #     # Filter tasks that contain any of the specified tags
    #     tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    #     if tag_list:
    #         # Use JSON_EXTRACT for SQLite JSON queries
    #         conditions = []
    #         for tag in tag_list:
    #             conditions.append(f"JSON_EXTRACT(tags, '$') LIKE '%\"{tag}\"%'")
    #         query = query.filter(db.or_(*[db.text(cond) for cond in conditions]))

    if priority:
        # Map priority to numeric values for comparison
        priority_order = {"low": 0, "medium": 1, "high": 2, "urgent": 3}
        min_priority_value = priority_order.get(priority, 0)
        priority_conditions = [
            Task.priority == p
            for p in priority_order
            if priority_order[p] >= min_priority_value
        ]
        query = query.where(or_(*priority_conditions))

    if due_before:
        query = query.where(Task.due_at < due_before)

    if due_after:
        query = query.where(Task.due_at > due_after)

    if updated_since:
        query = query.where(Task.updated_at > updated_since)

    # Apply sorting
    sort_column = getattr(Task, sort, Task.updated_at)
    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Execute query
    tasks = await db.execute(query.limit(limit))
    task_list = tasks.scalars().all()

    return TaskList(
        tasks=[TaskSchema.from_orm(task) for task in task_list],
        pagination={
            "has_more": len(task_list) == limit,
            "next_cursor": (
                f"offset_{len(task_list)}" if len(task_list) == limit else None
            ),
            "total_count": len(task_list),
        },
    )
