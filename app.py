import streamlit as st

from database.db import init_db, get_tasks, get_schedules, get_notes, update_task_status, delete_task
from agents.primary_agent import PrimaryAgent

init_db()

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AgentFlow",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%);
    border-right: 1px solid #2a2a4a;
}
[data-testid="stSidebar"] * { color: #e0e0f0 !important; }

/* Metric cards */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 10px;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    border-radius: 12px;
    margin-bottom: 8px;
}

/* Buttons in sidebar */
[data-testid="stSidebar"] button {
    background: rgba(99, 102, 241, 0.2) !important;
    border: 1px solid rgba(99, 102, 241, 0.4) !important;
    color: #a5b4fc !important;
    border-radius: 8px !important;
    font-size: 12px !important;
    text-align: left !important;
}
[data-testid="stSidebar"] button:hover {
    background: rgba(99, 102, 241, 0.4) !important;
}

.status-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}
.badge-pending   { background: #422006; color: #fb923c; }
.badge-completed { background: #052e16; color: #4ade80; }
.badge-high      { background: #450a0a; color: #f87171; }
.badge-medium    { background: #422006; color: #fb923c; }
.badge-low       { background: #052e16; color: #4ade80; }
</style>
""", unsafe_allow_html=True)

# ── Session state init ─────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = None
if "api_key_valid" not in st.session_state:
    st.session_state.api_key_valid = False
if "api_key_error" not in st.session_state:
    st.session_state.api_key_error = ""

def validate_and_connect(key: str):
    """Try a real Gemini call to validate the key before accepting it."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        m = genai.GenerativeModel("gemini-2.0-flash-lite")
        m.generate_content("Reply with the single word: OK")   # lightweight probe
        st.session_state.agent         = PrimaryAgent(key)
        st.session_state.api_key_valid = True
        st.session_state.api_key_error = ""
    except Exception as e:
        st.session_state.agent         = None
        st.session_state.api_key_valid = False
        st.session_state.api_key_error = str(e)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 AgentFlow")
    st.caption("Multi-Agent AI Task Manager")
    st.divider()

    # ── API Key section ──────────────────────────────────────────────────────
    st.markdown("### 🔑 Gemini API Key")

    if st.session_state.api_key_valid:
        # Show a green "connected" banner with a disconnect button
        st.markdown("""
        <div style="background:rgba(74,222,128,0.12);border:1px solid rgba(74,222,128,0.35);
                    border-radius:10px;padding:10px 14px;margin-bottom:8px;">
            <span style="color:#4ade80;font-weight:600;font-size:13px;">✅ Connected</span><br>
            <span style="color:#86efac;font-size:11px;">Gemini API key verified & active</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔌 Disconnect / Change Key", use_container_width=True):
            st.session_state.agent         = None
            st.session_state.api_key_valid = False
            st.session_state.api_key_error = ""
            st.rerun()
    else:
        # Input + validate button
        typed_key = st.text_input(
            "Enter your API key",
            type="password",
            placeholder="AIza...",
            label_visibility="collapsed"
        )
        st.caption("Get a free key → [aistudio.google.com](https://aistudio.google.com/app/apikey)")

        if st.button("🔍 Validate & Connect", use_container_width=True, type="primary"):
            if not typed_key.strip():
                st.warning("Please paste your API key first.")
            else:
                with st.spinner("Validating key with Gemini..."):
                    validate_and_connect(typed_key.strip())
                st.rerun()

        if st.session_state.api_key_error:
            st.markdown(f"""
            <div style="background:rgba(248,113,113,0.12);border:1px solid rgba(248,113,113,0.35);
                        border-radius:10px;padding:10px 14px;margin-top:6px;">
                <span style="color:#f87171;font-weight:600;font-size:12px;">❌ Validation failed</span><br>
                <span style="color:#fca5a5;font-size:11px;">{st.session_state.api_key_error[:120]}</span>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # Live dashboard metrics
    st.markdown("### 📊 Dashboard")
    tasks     = get_tasks()
    schedules = get_schedules()
    notes     = get_notes()
    pending   = [t for t in tasks if t[3] == "pending"]
    completed = [t for t in tasks if t[3] == "completed"]

    c1, c2 = st.columns(2)
    c1.metric("📋 Tasks",     len(tasks))
    c2.metric("⏳ Pending",   len(pending))
    c1.metric("📅 Events",    len(schedules))
    c2.metric("📝 Notes",     len(notes))

    st.divider()

    # Quick prompt examples
    st.markdown("### 💡 Quick Actions")
    examples = [
        "Add task: Fix login bug, high priority",
        "Show all my pending tasks",
        "Schedule team meeting on 2025-05-01 at 10:00",
        "Save a note: API uses REST with JSON responses",
        "What events do I have coming up?",
        "Mark task 1 as completed",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True, key=ex):
            st.session_state["prefill"] = ex

    st.divider()

    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Main area ──────────────────────────────────────────────────────────────────
st.markdown("# 🧠 AgentFlow Assistant")
st.caption("Powered by Gemini • Agents: Task Manager · Scheduler · Notes")
st.divider()

# Tabs: Chat | Tasks | Schedule | Notes
tab_chat, tab_tasks, tab_schedule, tab_notes = st.tabs(
    ["💬 Chat", "✅ Tasks", "📅 Schedule", "📝 Notes"]
)

# ── Chat Tab ───────────────────────────────────────────────────────────────────
with tab_chat:
    # Gate: remind user to connect if no agent yet
    if not st.session_state.api_key_valid:
        st.info("👈 Please enter and validate your Gemini API key in the sidebar to start chatting.")

    # Display full chat history
    for msg in st.session_state.messages:
        role = "assistant" if msg["role"] == "model" else msg["role"]
        with st.chat_message(role):
            st.markdown(msg["content"])

    # Handle prefill from sidebar quick-action buttons
    prefill    = st.session_state.pop("prefill", "")
    user_input = st.chat_input(
        "Ask your AI assistant anything...",
        disabled=not st.session_state.api_key_valid
    ) or prefill

    if user_input:
        if not st.session_state.agent:
            st.error("⚠️ Please validate your Gemini API key in the sidebar first.")
        else:
            # 1. Save & render user message
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            # 2. Call the primary agent and render the reply
            with st.chat_message("assistant"):
                with st.spinner("🤖 Agents working..."):
                    try:
                        reply = st.session_state.agent.run(
                            user_input,
                            st.session_state.messages[:-1]   # history without latest user msg
                        )
                    except Exception as e:
                        import traceback
                        reply = f"❌ **Agent error:** {e}\n\n```\n{traceback.format_exc()}\n```"

                st.markdown(reply)

            # 3. Save assistant reply AFTER rendering (so rerun shows it)
            st.session_state.messages.append({"role": "model", "content": reply})
            st.rerun()   # refresh sidebar metrics only — history is already saved above

# ── Tasks Tab ──────────────────────────────────────────────────────────────────
with tab_tasks:
    st.markdown("### Your Tasks")

    filter_status = st.radio("Filter:", ["All", "Pending", "Completed"],
                             horizontal=True, label_visibility="collapsed")

    all_tasks = get_tasks()
    if filter_status == "Pending":
        all_tasks = [t for t in all_tasks if t[3] == "pending"]
    elif filter_status == "Completed":
        all_tasks = [t for t in all_tasks if t[3] == "completed"]

    if not all_tasks:
        st.info("No tasks here yet. Ask the assistant to add one!")
    else:
        for t in all_tasks:
            tid, title, desc, status, priority, created = t
            with st.container():
                col1, col2, col3, col4 = st.columns([5, 2, 2, 1])
                with col1:
                    icon = "✅" if status == "completed" else "⏳"
                    st.markdown(f"**{icon} {title}**")
                    if desc:
                        st.caption(desc)
                with col2:
                    badge_class = f"badge-{priority}"
                    st.markdown(
                        f'<span class="status-badge {badge_class}">{priority.upper()}</span>',
                        unsafe_allow_html=True
                    )
                with col3:
                    badge_class = f"badge-{status}"
                    st.markdown(
                        f'<span class="status-badge {badge_class}">{status}</span>',
                        unsafe_allow_html=True
                    )
                with col4:
                    if status == "pending":
                        if st.button("✔", key=f"done_{tid}", help="Mark complete"):
                            update_task_status(tid, "completed")
                            st.rerun()
                    if st.button("🗑", key=f"del_{tid}", help="Delete"):
                        delete_task(tid)
                        st.rerun()
                st.markdown("---")

# ── Schedule Tab ───────────────────────────────────────────────────────────────
with tab_schedule:
    st.markdown("### Upcoming Schedule")
    schedules = get_schedules()
    if not schedules:
        st.info("No events scheduled. Ask the assistant to add one!")
    else:
        for s in schedules:
            sid, title, date, time, desc, created = s
            with st.container():
                cols = st.columns([6, 2, 2])
                with cols[0]:
                    st.markdown(f"**📅 {title}**")
                    if desc:
                        st.caption(desc)
                with cols[1]:
                    st.markdown(f"🗓 `{date}`")
                    if time:
                        st.markdown(f"⏰ `{time}`")
                st.markdown("---")

# ── Notes Tab ──────────────────────────────────────────────────────────────────
with tab_notes:
    st.markdown("### Saved Notes")
    notes = get_notes()
    if not notes:
        st.info("No notes saved yet. Ask the assistant to save one!")
    else:
        for n in notes:
            nid, title, content, tags, created = n
            with st.expander(f"📝 {title}"):
                if content:
                    st.write(content)
                if tags:
                    for tag in tags.split(","):
                        st.markdown(
                            f'<span class="status-badge badge-medium">#{tag.strip()}</span>&nbsp;',
                            unsafe_allow_html=True
                        )
                st.caption(f"Saved: {created}")
