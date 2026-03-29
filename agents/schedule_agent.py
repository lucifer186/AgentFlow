from database.db import add_schedule, get_schedules, delete_schedule


class ScheduleAgent:
    """Sub-agent responsible for calendar and scheduling operations."""

    def execute(self, function_name: str, args: dict) -> str:
        if function_name == "add_schedule":
            return add_schedule(
                title=args.get("title", "Untitled Event"),
                date=args.get("date", ""),
                time=args.get("time", ""),
                description=args.get("description", "")
            )

        elif function_name == "get_schedules":
            rows = get_schedules()
            if not rows:
                return "No schedules found."
            lines = []
            for r in rows:
                time_str = f"@ {r[3]}" if r[3] else ""
                desc_str = f"— {r[4]}" if r[4] else ""
                lines.append(f"📅 [{r[0]}] {r[1]} on {r[2]} {time_str} {desc_str}".strip())
            return "\n".join(lines)

        elif function_name == "delete_schedule":
            return delete_schedule(args.get("schedule_id"))

        return f"ScheduleAgent: unknown function '{function_name}'."
