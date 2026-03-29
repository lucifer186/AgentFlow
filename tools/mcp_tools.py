# MCP-style tool definitions — passed to Gemini as function declarations

MCP_TOOLS = [
    {
        "name": "add_task",
        "description": "Add a new task to the task manager",
        "parameters": {
            "type": "object",
            "properties": {
                "title":       {"type": "string", "description": "Task title"},
                "description": {"type": "string", "description": "Task details"},
                "priority":    {"type": "string", "description": "low / medium / high"}
            },
            "required": ["title"]
        }
    },
    {
        "name": "get_tasks",
        "description": "Retrieve all tasks or filter by status (pending/completed)",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "description": "pending or completed (optional)"}
            }
        }
    },
    {
        "name": "complete_task",
        "description": "Mark a task as completed by its ID",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "ID of the task to complete"}
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "delete_task",
        "description": "Delete a task by its ID",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "ID of the task to delete"}
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "add_schedule",
        "description": "Add a calendar event or schedule entry",
        "parameters": {
            "type": "object",
            "properties": {
                "title":       {"type": "string", "description": "Event title"},
                "date":        {"type": "string", "description": "Date in YYYY-MM-DD format"},
                "time":        {"type": "string", "description": "Time in HH:MM format (optional)"},
                "description": {"type": "string", "description": "Event description (optional)"}
            },
            "required": ["title", "date"]
        }
    },
    {
        "name": "get_schedules",
        "description": "Get all upcoming schedules and calendar events",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "add_note",
        "description": "Save a note with optional tags",
        "parameters": {
            "type": "object",
            "properties": {
                "title":   {"type": "string", "description": "Note title"},
                "content": {"type": "string", "description": "Note content"},
                "tags":    {"type": "string", "description": "Comma-separated tags (optional)"}
            },
            "required": ["title"]
        }
    },
    {
        "name": "get_notes",
        "description": "Retrieve all saved notes",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
]
