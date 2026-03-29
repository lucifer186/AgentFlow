from database.db import add_task, get_tasks, update_task_status, delete_task


class TaskAgent:
    """Sub-agent responsible for all task management operations."""

    def execute(self, function_name: str, args: dict) -> str:
        if function_name == "add_task":
            return add_task(
                title=args.get("title", "Untitled"),
                description=args.get("description", ""),
                priority=args.get("priority", "medium")
            )

        elif function_name == "get_tasks":
            rows = get_tasks(status=args.get("status"))
            if not rows:
                return "No tasks found."
            lines = []
            for r in rows:
                icon = "✅" if r[3] == "completed" else "⏳"
                lines.append(f"{icon} [{r[0]}] {r[1]} | priority: {r[4]} | status: {r[3]}")
            return "\n".join(lines)

        elif function_name == "complete_task":
            return update_task_status(args.get("task_id"), "completed")

        elif function_name == "delete_task":
            return delete_task(args.get("task_id"))

        return f"TaskAgent: unknown function '{function_name}'."
