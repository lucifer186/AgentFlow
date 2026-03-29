import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool

from tools.mcp_tools import MCP_TOOLS
from agents.task_agent import TaskAgent
from agents.schedule_agent import ScheduleAgent
from agents.notes_agent import NotesAgent

# Maps each tool name → responsible sub-agent
TOOL_ROUTING = {
    "add_task":        "task",
    "get_tasks":       "task",
    "complete_task":   "task",
    "delete_task":     "task",
    "add_schedule":    "schedule",
    "get_schedules":   "schedule",
    "delete_schedule": "schedule",
    "add_note":        "notes",
    "get_notes":       "notes",
    "delete_note":     "notes",
}


class PrimaryAgent:
    """
    Orchestrator agent.
    Sends user message to Gemini with MCP tools, dispatches
    function calls to sub-agents, loops until a text reply is returned.
    """

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.api_key        = api_key
        self.task_agent     = TaskAgent()
        self.schedule_agent = ScheduleAgent()
        self.notes_agent    = NotesAgent()

    def _get_model(self):
        """Build a GenerativeModel with tools attached."""
        tools = [Tool(function_declarations=[
            FunctionDeclaration(
                name=t["name"],
                description=t["description"],
                parameters=t["parameters"]
            )
            for t in MCP_TOOLS
        ])]
        return genai.GenerativeModel(
            model_name="gemini-2.0-flash-lite",
            tools=tools,
            system_instruction=(
                "You are AgentFlow, a helpful AI assistant that manages tasks, "
                "schedules, and notes for the user. "
                "When the user asks you to do something, always use the available "
                "tools to carry it out — never just describe what you would do. "
                "After calling a tool, confirm what you did in a friendly, concise way."
            )
        )

    def _route_tool(self, fn_name: str, args: dict) -> str:
        """Dispatch a function call to the correct sub-agent."""
        agent_type = TOOL_ROUTING.get(fn_name)
        if agent_type == "task":
            return self.task_agent.execute(fn_name, args)
        elif agent_type == "schedule":
            return self.schedule_agent.execute(fn_name, args)
        elif agent_type == "notes":
            return self.notes_agent.execute(fn_name, args)
        return f"No agent registered for tool '{fn_name}'."

    def _extract_fn_call(self, response):
        """Return the first function_call part, or None."""
        try:
            for part in response.candidates[0].content.parts:
                fc = getattr(part, "function_call", None)
                if fc and fc.name:
                    return fc
        except (IndexError, AttributeError):
            pass
        return None

    def _extract_text(self, response) -> str:
        """Return the first text part from the response."""
        try:
            for part in response.candidates[0].content.parts:
                text = getattr(part, "text", None)
                if text:
                    return text
        except (IndexError, AttributeError):
            pass
        return ""

    def run(self, user_message: str, chat_history: list) -> str:
        """
        Agentic loop:
        1. Send user message to Gemini
        2. If Gemini calls a tool → execute via sub-agent → send result back
        3. Repeat until Gemini returns plain text (max 6 tool calls)
        """
        model = self._get_model()

        # Build clean history — only plain text turns, correct roles
        history = []
        for msg in chat_history:
            role    = msg.get("role", "user")
            if role == "assistant":
                role = "model"
            if role not in ("user", "model"):
                role = "user"
            content = msg.get("content", "").strip()
            if content:
                history.append({"role": role, "parts": [{"text": content}]})

        chat = model.start_chat(history=history)

        # First Gemini call
        try:
            response = chat.send_message(user_message)
        except Exception as e:
            return f"❌ Gemini error on send: {e}"

        # Agentic tool loop
        for _step in range(6):
            fn_call = self._extract_fn_call(response)

            if fn_call is None:
                # No more tool calls — return the final reply
                text = self._extract_text(response)
                return text if text else "✅ Done."

            # Execute the tool
            fn_name     = fn_call.name
            args        = dict(fn_call.args)
            tool_result = self._route_tool(fn_name, args)

            # Return tool result to Gemini using a plain dict (works in all SDK versions)
            try:
                response = chat.send_message([{
                    "function_response": {
                        "name": fn_name,
                        "response": {"result": tool_result}
                    }
                }])
            except Exception as e:
                # Tool ran fine — just couldn't get follow-up from Gemini
                return f"✅ {tool_result}\n\n_(Follow-up error: {e})_"

        return "⚠️ Agent reached the maximum number of steps."
