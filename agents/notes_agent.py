from database.db import add_note, get_notes, delete_note


class NotesAgent:
    """Sub-agent responsible for notes management."""

    def execute(self, function_name: str, args: dict) -> str:
        if function_name == "add_note":
            return add_note(
                title=args.get("title", "Untitled Note"),
                content=args.get("content", ""),
                tags=args.get("tags", "")
            )

        elif function_name == "get_notes":
            rows = get_notes()
            if not rows:
                return "No notes found."
            lines = []
            for r in rows:
                preview = (r[2] or "")[:80]
                tags_str = f" | tags: {r[3]}" if r[3] else ""
                lines.append(f"📝 [{r[0]}] {r[1]}: {preview}...{tags_str}")
            return "\n".join(lines)

        elif function_name == "delete_note":
            return delete_note(args.get("note_id"))

        return f"NotesAgent: unknown function '{function_name}'."
