import streamlit as st
import sqlite3
from pathlib import Path
import random
import time
from datetime import datetime, timedelta
import pytz

# ----------------- Setup DB -----------------
DB_FILE = Path("tasks.db")

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                user_name TEXT NOT NULL
            )
        """)
        conn.commit()

init_db()

# ----------------- Page Setup -----------------
st.set_page_config(page_title="SmartTaskBot", page_icon="✨", layout="centered")

# ----------------- Styles -----------------
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;500&display=swap');

        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
            background-color: #fffaf3;
            color: #222 !important;
        }

        .header {
            font-size: 36px;
            text-align: center;
            color: #111 !important;
            margin-bottom: 5px;
        }

        .subtext {
            text-align: center;
            font-size: 17px;
            color: #333 !important;
        }

        .card {
            background-color: #f0f8ff;
            color: #111 !important;
            padding: 15px 20px;
            border-left: 5px solid #4da6ff;
            border-radius: 10px;
            margin: 15px 0;
        }

        .soft-block {
            background-color: #fef6ff;
            padding: 20px;
            border-radius: 12px;
            color: #111 !important;
            margin: 20px 0;
        }

        .emoji-banner {
            text-align: center;
            font-size: 28px;
            margin-top: 10px;
            color: #111 !important;
        }

        input, textarea, label, div[class*="stCheckbox"] label {
            color: #111 !important;
        }

        .stTextInput > div > div > input {
            background-color: #fff !important;
            color: #111 !important;
            border: 1px solid #ccc;
        }

        .stTextArea textarea {
            background-color: #fff !important;
            color: #111 !important;
            border: 1px solid #ccc;
        }

        .css-1cpxqw2, .stMarkdown p, .stButton>button {
            color: #111 !important;
        }

    </style>
""", unsafe_allow_html=True)
# ----------------- Header -----------------
st.markdown("<div class='header'>✨ SmartTaskBot✨</div>", unsafe_allow_html=True)
st.markdown("<div class='subtext'>Gentle planning, made for your mood.</div>", unsafe_allow_html=True)

# ----------------- Quote -----------------
quotes = [
    "“Small steps every day lead to big change.”",
    "“You don’t need to do everything — just something.”",
    "“Even one task done is progress.”",
    "“Work gently. Rest proudly.”",
    "“Start where you are. Use what you have. Do what you can.”"
]
st.markdown(f"<div class='quote'>{random.choice(quotes)}</div>", unsafe_allow_html=True)

# ----------------- Reminder -----------------
reminders = [
    "Take a deep breath and stretch a little.",
    "Stay hydrated — drink some water.",
    "Don’t forget your lunch today!",
    "Your mind is powerful — even if you're tired.",
    "Try to take a 5-minute break after every hour.",
    "Smile! You're doing better than you think."
]

if 'last_reminder_time' not in st.session_state:
    st.session_state['last_reminder_time'] = time.time()

if time.time() - st.session_state['last_reminder_time'] > 0:
    st.markdown(f"<div class='card reminder'>🧘 {random.choice(reminders)}</div>", unsafe_allow_html=True)
    st.session_state['last_reminder_time'] = time.time()

# ----------------- Preferences -----------------
with st.expander("⚙ Preferences"):
    name = st.text_input("Your Name (optional)", placeholder="e.g., Anicka")
    timezone_list = pytz.all_timezones
    selected_tz = st.selectbox("Your Timezone", timezone_list, index=timezone_list.index("Asia/Kolkata"))
    st.caption("Used to plan your day in your local time")

user_name = name.strip().lower() if name.strip() else "guest_user"
now = datetime.now(pytz.timezone(selected_tz))
greeting_time = now.strftime("%A, %I:%M %p")

if name.strip():
    st.markdown(f"<div class='emoji-banner'>Hi <b>{name.strip().title()}</b> — {greeting_time}</div>", unsafe_allow_html=True)
else:
    st.markdown(f"<div class='emoji-banner'>Hi there! — {greeting_time}</div>", unsafe_allow_html=True)

# ----------------- Help Section -----------------
with st.expander("ℹ How to Use SmartTaskBot"):
    st.markdown("""
    - *Enter your name* (optional) and timezone.
    - *Type your tasks* in any format — new lines, commas, or semicolons.
    - *Plan My Day* will organize tasks based on your energy level.
    - *Add to My Tasks* saves them so you can track or mark them later.
    - *Mark as Done* appears after adding tasks.
    - *Need Help?!
    """)

# ----------------- Mood + Task Input -----------------
st.markdown("<div class='soft-block'>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    mood = st.radio("How are you feeling today?", ["Energetic ⚡", "Neutral ☁", "Tired 💤"])
with col2:
    raw_input = st.text_area("📝 Enter tasks (in any format)", placeholder="e.g., Finish report\nBuy milk; call mom")

st.caption("Tip: You can write tasks in any way — we’ll organize it!")

st.markdown("</div>", unsafe_allow_html=True)

# ----------------- Task Processing -----------------
# Accept tasks in any format (comma, newline, semicolon)
def parse_tasks(text):
    splitters = [',', ';', '\n']
    for sep in splitters:
        text = text.replace(sep, ',')
    return [t.strip() for t in text.split(',') if t.strip()]

parsed_tasks = parse_tasks(raw_input)
parsed_objects = [{"text": t, "done": False, "created_at": now.strftime("%Y-%m-%d %H:%M:%S")} for t in parsed_tasks]

# ----------------- DB Functions -----------------
def get_all_tasks(user_name):
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM tasks WHERE user_name = ?", (user_name,)).fetchall()
        return [dict(row) for row in rows]

def add_task(text, user_name):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("INSERT INTO tasks (text, done, created_at, user_name) VALUES (?, ?, ?, ?)",
                     (text, False, datetime.now().isoformat(), user_name))
        conn.commit()

def clear_all_tasks(user_name):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("DELETE FROM tasks WHERE user_name = ?", (user_name,))
        conn.commit()

def update_task_status(task_id, done):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("UPDATE tasks SET done = ? WHERE id = ?", (done, task_id))
        conn.commit()

# ----------------- Current Task Pool -----------------
saved_tasks = get_all_tasks(user_name)
existing_texts = [t["text"].lower() for t in saved_tasks]
current_tasks = parsed_objects if parsed_tasks else saved_tasks

# ----------------- Buttons: PLAN → ADD → CLEAR -----------------
col_plan, col_add, col_clear = st.columns(3)
with col_plan:
    plan_clicked = st.button("✨ Plan My Day")

with col_add:
    if st.button("📌 Add to My Tasks"):
        if parsed_tasks:
            added = False
            for task in parsed_tasks:
                if task.lower() not in existing_texts:
                    add_task(task, user_name)
                    added = True
            if added:
                st.success("Tasks added successfully!")
            else:
                st.info("No new tasks to add.")
        else:
            st.warning("Please enter tasks first.")

with col_clear:
    if st.button("🧹 Clear All Tasks"):
        clear_all_tasks(user_name)
        st.success("Your saved tasks have been cleared.")
        st.rerun()
        
# ----------------- Task Intensity -----------------
def estimate_duration(text):
    lower = text.lower()
    if any(w in lower for w in ["report", "presentation", "debug", "analyze", "fix"]):
        return 45
    elif any(w in lower for w in ["homework", "review", "prepare", "write"]):
        return 30
    else:
        return 15

# ----------------- Mood-Based Filtering -----------------
def mood_filter(tasks, mood):
    def get_level(text):
        lower = text.lower()
        if any(w in lower for w in ["report", "presentation", "fix", "debug"]):
            return "high"
        elif any(w in lower for w in ["review", "homework", "write"]):
            return "medium"
        else:
            return "low"

    def keep(task):
        level = get_level(task["text"])
        if mood == "Tired 💤" and level in ["high", "medium"]:
            return False
        if mood == "Neutral ☁" and level == "high":
            return False
        return True

    return [t for t in tasks if keep(t)]

# ----------------- Generate Schedule -----------------
def generate_schedule(tasks):
    start_time = datetime.now(pytz.timezone(selected_tz)).replace(second=0, microsecond=0)
    schedule = []
    current = start_time

    for task in tasks:
        duration = estimate_duration(task["text"])
        end = current + timedelta(minutes=duration)
        schedule.append({
            "time": f"{current.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}",
            "text": task["text"],
            "emoji": "🔥" if duration > 30 else "📚" if duration == 30 else "✅"
        })
        current = end

        # Insert break every hour
        if (current - start_time).seconds % 3600 == 0:
            schedule.append({
                "time": f"{current.strftime('%I:%M %p')} - {(current + timedelta(minutes=5)).strftime('%I:%M %p')}",
                "text": "Break ☕",
                "emoji": "☕"
            })
            current += timedelta(minutes=5)

    return schedule

# ----------------- Show Smart Plan -----------------
if plan_clicked:
    if not current_tasks:
        st.warning("No tasks found. Please enter or save tasks first.")
    else:
        mood_tasks = mood_filter(current_tasks, mood)
        plan = generate_schedule(mood_tasks)

        if plan:
            st.markdown("### 🗓 Your Smart Day Plan")
            for p in plan:
                st.markdown(f"<div class='card'>{p['time']} → {p['text']} {p['emoji']}</div>", unsafe_allow_html=True)
        else:
            st.info("No tasks matched your current mood energy level.")

# ----------------- Mark As Done & Suggestions -----------------
if saved_tasks:
    st.markdown("### ✅ Mark Your Completed Tasks")
    task_done = False
    for task in saved_tasks:
        checked = st.checkbox(task["text"], value=task["done"], key=f"task_{task['id']}")
        if checked != task["done"]:
            update_task_status(task["id"], checked)
            task_done = True

    if task_done:
        st.success("Great job! You completed a task!")
        st.balloons()

    # ----------------- Smart Suggestions -----------------
    st.markdown("### ✨ Need Help With a Task?")
    suggestion_map = {
        "email": f"Subject: Follow-up\n\nHi [Name],\nJust checking in on [topic]. Let me know your thoughts.\n\nThanks,\n{name.strip().title()}",
        "call": "Call script: Hi! Just wanted to connect quickly about [topic]. Is now a good time?",
        "meeting": "Meeting Outline:\n- Agenda overview\n- Discussion\n- Action steps\n- Q&A",
        "homework": "Try: 25 mins focused study + 5 min break. Repeat 3x. Pomodoro works wonders!",
        "clean": "Tip: Play a 10-minute timer and clean one area. Small wins = motivation!"
    }

    keywords = {
        "email": ["email", "mail", "send", "reply"],
        "call": ["call", "phone", "speak"],
        "meeting": ["meeting", "zoom", "call", "agenda"],
        "homework": ["study", "homework", "assignment"],
        "clean": ["clean", "organize", "declutter"]
    }

    for task in saved_tasks:
        task_lower = task["text"].lower()
        for category, keys in keywords.items():
            if any(k in task_lower for k in keys):
                with st.expander(f"💡 Help with: {task['text']}"):
                    st.code(suggestion_map[category], language="markdown")
                break
else:
    st.info("💡 To mark tasks as done or see suggestions, please add tasks to your day.")
