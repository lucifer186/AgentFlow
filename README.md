# 🤖 AgentFlow — Multi-Agent AI Task Manager

A multi-agent AI system built with **Streamlit + Gemini API + SQLite** that helps you manage tasks, schedules, and notes through natural language.

---

## 🏗️ Architecture

```
User Message
     │
     ▼
PrimaryAgent (Gemini orchestrator)
  ├─ MCP Tool: add_task / get_tasks / complete_task  →  TaskAgent     →  SQLite (tasks)
  ├─ MCP Tool: add_schedule / get_schedules          →  ScheduleAgent →  SQLite (schedules)
  └─ MCP Tool: add_note / get_notes                  →  NotesAgent    →  SQLite (notes)
     │
     ▼
Final natural-language response → Streamlit UI
```

---

## 🚀 Setup (Windows + VS Code)

### Step 1 — Open project in VS Code
```
File → Open Folder → select multi-agent-task-manager
```

### Step 2 — Create virtual environment
```bash
python -m venv venv
```

### Step 3 — Activate virtual environment
```bash
venv\Scripts\activate
```
> In VS Code: `Ctrl+Shift+P` → "Python: Select Interpreter" → choose `.\venv\`

### Step 4 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 5 — Add your Gemini API key
Copy `.env.example` to `.env` and add your key:
```
GEMINI_API_KEY=your_gemini_api_key_here
```
> Get a free key at: https://aistudio.google.com/app/apikey

### Step 6 — Run the app
```bash
streamlit run app.py
```
Open: http://localhost:8501

---

## ☁️ Deploy to Streamlit Cloud (Free)

1. Push to GitHub (the `.gitignore` already excludes `.env` and `venv/`)
2. Go to https://streamlit.io/cloud → Sign in with GitHub
3. Click **New app** → select your repo → entry point: `app.py`
4. Under **Secrets**, add:
   ```toml
   GEMINI_API_KEY = "your_key_here"
   ```
5. Click **Deploy** — live in ~2 minutes!

---

## 💬 Example Prompts

- `Add task: Review pull request, high priority`
- `Show all my pending tasks`
- `Schedule team standup on 2025-05-01 at 09:00`
- `Save a note: The API uses REST with JSON responses, tags: api, backend`
- `What events do I have coming up?`
- `Mark task 1 as completed`
- `Add a task and schedule a review meeting for it next Monday`

---

## 📁 Project Structure

```
multi-agent-task-manager/
├── app.py                  # Streamlit UI (main entry point)
├── agents/
│   ├── primary_agent.py    # Gemini orchestrator + agentic loop
│   ├── task_agent.py       # Task CRUD operations
│   ├── schedule_agent.py   # Schedule/calendar operations
│   └── notes_agent.py      # Notes operations
├── tools/
│   └── mcp_tools.py        # MCP-style tool definitions for Gemini
├── database/
│   └── db.py               # SQLite setup and helpers
├── requirements.txt
├── .env.example
└── .gitignore
```
