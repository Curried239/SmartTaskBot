import streamlit as st
import sqlite3
from pathlib import Path
import random
import time
from datetime import datetime, timedelta
import re
import json

# ----------------- SQLite Functions -----------------
DB_FILE = Path("tasks.db")

# ----------------- SQLite Functions -----------------
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_info (
                id INTEGER PRIMARY KEY,
                name TEXT,
                mood TEXT
            )
        """)
        user = conn.execute("SELECT * FROM user_info WHERE id = 1").fetchone()
        if not user:
            conn.execute("INSERT INTO user_info (id, name, mood) VALUES (1, '', '')")
        conn.commit()

def add_task(text):
    with sqlite3.connect(DB_FILE) as conn:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute("INSERT INTO tasks (text, done, created_at) VALUES (?, 0, ?)", (text, now))
        conn.commit()

def get_all_tasks():
    with sqlite3.connect(DB_FILE) as conn:
        rows = conn.execute("SELECT id, text, done, created_at FROM tasks").fetchall()
        return [{"id": row[0], "text": row[1], "done": bool(row[2]), "created_at": row[3]} for row in rows]

def update_task_status(task_id, done):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("UPDATE tasks SET done = ? WHERE id = ?", (done, task_id))
        conn.commit()

def clear_all_tasks():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("DELETE FROM tasks")
        conn.commit()
        

def get_user_info():
    with sqlite3.connect(DB_FILE) as conn:
        result = conn.execute("SELECT name, mood FROM user_info WHERE id = 1").fetchone()
        return {"name": result[0], "mood": result[1]} if result else {"name": "", "mood": ""}

def update_user_info(name, mood):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("UPDATE user_info SET name = ?, mood = ? WHERE id = 1", (name, mood))
        conn.commit()
# ----------------- Initialize -----------------
init_db()
user_info = get_user_info()

# Load custom font
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
    <style>
        h1, h2, h3, h4, h5 {
            color: #f5a623;
        }
        .stTextInput > div > div > input {
            background-color: #333 !important;
            color: #fefefe !important;
            border: 1px solid #555;
        }
        .stTextArea textarea {
            background-color: #333 !important;
            color: #fefefe !important;
        }
        .stButton>button {
            background-color: #f5a623;
            color: black;
            border-radius: 8px;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #f7c65b;
            color: black;
        }
        .emoji-banner {
            font-size: 32px;
            text-align: right;
            margin-top: -40px;
            margin-right: 10px;
            animation: float 3s ease-in-out infinite;
        }
        @keyframes float {
            0% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
            100% { transform: translateY(0); }
        }
    </style>
""", unsafe_allow_html=True)


# ----------------- SmartCare Reminders -----------------
reminders = [
    "Take a deep breath and stretch a little!",
    "Stay hydrated — a glass of water never hurts.",
    "You’re doing amazing. Consider a 5-minute break?",
    "Even small steps count — keep going at your pace.",
    "Don’t forget to smile today. You’re making progress!"
]

if 'last_reminder_time' not in st.session_state:
    st.session_state['last_reminder_time'] = time.time()

if time.time() - st.session_state['last_reminder_time'] > 0:
    st.sidebar.info(random.choice(reminders))
    st.session_state['last_reminder_time'] = time.time()

# ----------------- UI -----------------
    # Top Branding Header
st.markdown("<h1 style='text-align: center;'>✨ SmartTaskBot</h1>", unsafe_allow_html=True)
st.caption("Your gentle AI planner with mood-aware scheduling")

name = st.text_input("What's your name?", value=user_info["name"])
mood_options = ["Energetic ⚡", "Neutral ☁", "Tired 💤"]
mood_index = mood_options.index(user_info["mood"]) if user_info["mood"] in mood_options else 0
mood = st.radio("How are you feeling today?", mood_options, index=mood_index)

update_user_info(name.strip(), mood)

greeting = datetime.now().strftime("%A, %I:%M %p")
if name.strip():
    st.subheader(f"Hi {name.strip().title()} — Today is {greeting}. Let’s gently plan your day.")
else:
    st.subheader(f"Today is {greeting}. Let’s gently plan your day.")

# Mood-based emoji banner
mood_emoji = {
    "Energetic ⚡": "⚡",
    "Neutral ☁": "☁",
    "Tired 💤": "💤"
}
if mood in mood_emoji:
    st.markdown(f"<div class='emoji-banner'>{mood_emoji[mood]}</div>", unsafe_allow_html=True)

# ----------------- Task Input -----------------
tasks_input = st.text_area("📝 Enter tasks (comma-separated):", placeholder="e.g., finish homework, clean room")

# Load tasks from DB
existing_tasks = get_all_tasks()
existing_texts = [t["text"].strip().lower() for t in existing_tasks]

if st.button("Add to My Day"):
    if tasks_input.strip():
        new_tasks = [task.strip() for task in tasks_input.split(",") if task.strip()]
        added = False
        for task in new_tasks:
            if task.lower() not in existing_texts:
                add_task(task)
                added = True
        if added:
            st.success("Tasks added to your day!")
        else:
            st.warning("All entered tasks already exist.")
    else:
        st.warning("Please enter at least one task.")

if st.button("Clear My Tasks ❌"):
    clear_all_tasks()
    st.success("Your task list has been cleared!")
# ----------------- Helper: Estimate Duration -----------------
def estimate_duration(text):
    high_keywords = ["report", "presentation", "debug", "analyze", "fix", "project"]
    medium_keywords = ["homework", "write", "review", "prepare"]
    low_keywords = ["email", "call", "reply", "clean", "read"]

    lower = text.lower()
    if any(word in lower for word in high_keywords):
        return 45
    elif any(word in lower for word in medium_keywords):
        return 30
    else:
        return 15

# ----------------- Timeline Generator -----------------
def generate_schedule(tasks):
    now = datetime.now().replace(second=0, microsecond=0)
    schedule = []
    used_slots = set()
    last_time = now

    # Remove done tasks
    tasks = [t for t in tasks if not t["done"]]

    # Sort by created_at
    tasks = sorted(tasks, key=lambda x: x["created_at"])

    for task in tasks:
        duration = estimate_duration(task["text"])
        start = last_time
        end = start + timedelta(minutes=duration)

        schedule.append({
            "time": f"{start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}",
            "text": task["text"],
            "emoji": "✅" if duration <= 15 else "📚" if duration <= 30 else "🔥"
        })
        last_time = end

        # Insert breaks every hour
        if (last_time - now).seconds % 3600 == 0:
            schedule.append({
                "time": f"{last_time.strftime('%I:%M %p')} - {(last_time + timedelta(minutes=5)).strftime('%I:%M %p')}",
                "text": "Break ☕",
                "emoji": "☕"
            })
            last_time += timedelta(minutes=5)

    # Insert fixed meal times
    def insert_meal(target_time, label, icon):
        meal_time = now.replace(hour=target_time, minute=0)
        if meal_time > now and all(meal_time.strftime('%I:%M %p') not in s["time"] for s in schedule):
            schedule.append({
                "time": f"{meal_time.strftime('%I:%M %p')} - {(meal_time + timedelta(minutes=30)).strftime('%I:%M %p')}",
                "text": label,
                "emoji": icon
            })

    insert_meal(9, "Breakfast 🥣", "🥣")
    insert_meal(13, "Lunch 🍽", "🍽")
    insert_meal(20, "Dinner 🍛", "🍛")
    insert_meal(18, "Wrap-up your day 🌙", "🌙")

    # Final sort by time
    schedule = sorted(schedule, key=lambda x: datetime.strptime(x["time"].split(" - ")[0], "%I:%M %p"))
    return schedule

# ----------------- Prioritize & Display Smart Day Plan -----------------
if st.button("Prioritize My Day 💡"):
    # Step 1: Use typed input if present, else use DB tasks
    input_tasks = [task.strip() for task in tasks_input.split(",") if task.strip()]
    use_input = bool(input_tasks)

    if use_input:
        task_list = [{"text": t, "done": False, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")} for t in input_tasks]
    else:
        task_list = get_all_tasks()
        task_list = [t for t in task_list if not t["done"]]  # Only show incomplete tasks

    if not task_list:
        st.warning("Please enter tasks or use 'Add to My Day' first.")
    else:
        # Step 2: Filter by energy level
        def get_intensity(text):
            text = text.lower()
            if any(x in text for x in ["debug", "report", "analyze", "fix"]):
                return "high"
            elif any(x in text for x in ["write", "homework", "review"]):
                return "medium"
            else:
                return "low"

        def mood_filter(task):
            level = get_intensity(task["text"])
            if mood == "Tired 💤" and level in ["medium", "high"]:
                return False
            if mood == "Neutral ☁" and level == "high":
                return False
            return True

        filtered_tasks = [t for t in task_list if mood_filter(t)]

        # Step 3: Generate and show schedule
        def estimate_duration(text):
            level = get_intensity(text)
            return 45 if level == "high" else 30 if level == "medium" else 15

        def generate_schedule(tasks):
            now = datetime.now().replace(second=0, microsecond=0)
            last_time = now
            plan = []

            for task in tasks:
                duration = estimate_duration(task["text"])
                start = last_time
                end = start + timedelta(minutes=duration)
                plan.append({
                    "time": f"{start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}",
                    "text": task["text"],
                    "emoji": "🔥" if duration > 30 else "📚" if duration == 30 else "✅"
                })
                last_time = end

                if (last_time - now).seconds % 3600 == 0:
                    plan.append({
                        "time": f"{last_time.strftime('%I:%M %p')} - {(last_time + timedelta(minutes=5)).strftime('%I:%M %p')}",
                        "text": "Break ☕",
                        "emoji": "☕"
                    })
                    last_time += timedelta(minutes=5)

            return plan

        schedule = generate_schedule(filtered_tasks)

        st.markdown("### 🕒 Your Smart Day Plan")
        if schedule:
            for item in schedule:
                st.write(f"{item['time']} → {item['text']} {item['emoji']}")
        else:
            st.info("No tasks matched your current energy level.")
# ----------------- Smart Suggestions -----------------
st.markdown("### ✨ Need Help With Any Task?")

suggestion_map = {
    "email": f"Subject: Following up on [topic]\n\nHi [Recipient's Name],\n\nI hope this message finds you well. I just wanted to follow up regarding [your task].\n\nPlease let me know if you need anything from my side.\n\nWarm regards,\n{name.strip().title() if name.strip() else '[Your Name]'}",
    "call": "Hi [Name], just wanted to check if we can catch up on [topic]. Let me know a good time to call.",
    "meeting": "Meeting Agenda:\n1. Review [topic]\n2. Discuss next steps\n3. Q&A\n\nDuration: 30 minutes",
    "homework": "Try this:\n- Study for 25 minutes\n- 5-minute break\n- Repeat 2-3 times\n\nYou’ve got this!",
    "grocery": "Grocery List:\n- Milk\n- Bread\n- Fruits\n- Eggs\n\nTip: Use a note app while shopping!",
    "clean": "Set a 10-minute timer, put on music, and clean one surface at a time. You’ll feel better after even 10 minutes!"
}

task_keywords = {
    "email": ["email", "mail", "message", "send", "reply"],
    "call": ["call", "phone", "talk", "speak"],
    "meeting": ["meeting", "zoom", "appointment", "schedule"],
    "homework": ["homework", "study", "assignment", "prepare"],
    "grocery": ["grocery", "shopping", "buy", "purchase"],
    "clean": ["clean", "organize", "tidy", "declutter"]
}

# Use either typed tasks or DB
all_suggestions = (
    [{"text": t.strip()} for t in tasks_input.split(",") if t.strip()]
    if tasks_input.strip()
    else get_all_tasks()
)

for task in all_suggestions:
    task_lower = task["text"].lower()
    for category, keywords in task_keywords.items():
        if any(word in task_lower for word in keywords):
            with st.expander(f"Need help with: '{task['text']}'"):
                if st.button(f"Show suggestion for: {task['text']}", key=f"suggest_{task['text']}"):
                    st.code(suggestion_map[category], language="markdown")
            break


# ----------------- Mark as Done -----------------
task_completed = False

st.markdown("### ☑ Mark Your Completed Tasks")
for task in get_all_tasks():
    new_status = st.checkbox(task["text"], value=task["done"], key=f"task_{task['id']}")
    if new_status != task["done"]:
        update_task_status(task["id"], new_status)
        task_completed = True

if task_completed:
    st.success("👏 You completed a task!")
    st.balloons()