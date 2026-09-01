// API types matching the backend schemas

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: 'todo' | 'doing' | 'blocked' | 'done' | 'archived';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  due_at?: string; // ISO datetime string
  tags: string[];
  context: 'personal' | 'professional' | 'mixed';
  workspace?: string;
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
  completed_at?: string; // ISO datetime string
}

export interface TaskCreate {
  title: string;
  description?: string;
  status?: 'todo' | 'doing' | 'blocked' | 'done' | 'archived';
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  due_at?: string;
  tags?: string[];
  context?: 'personal' | 'professional' | 'mixed';
  workspace?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: 'todo' | 'doing' | 'blocked' | 'done' | 'archived';
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  due_at?: string;
  tags?: string[];
  context?: 'personal' | 'professional' | 'mixed';
  workspace?: string;
}

export interface TaskList {
  tasks: Task[];
  pagination: {
    has_more: boolean;
    next_cursor?: string;
    total_count: number;
  };
}

export interface HealthResponse {
  status: string;
  version: string;
  database: string;
  timestamp: string;
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

// Query parameters for task listing
export interface TaskFilters {
  status?: string;
  context?: string;
  tags?: string;
  priority?: string;
  due_before?: string;
  due_after?: string;
  updated_since?: string;
}

export interface TaskSorting {
  sort?: 'created_at' | 'updated_at' | 'due_at' | 'priority' | 'title';
  order?: 'asc' | 'desc';
}

export interface TaskPagination {
  limit?: number;
  cursor?: string;
}

// Combined query parameters
export interface TaskQuery extends TaskFilters, TaskSorting, TaskPagination {}
