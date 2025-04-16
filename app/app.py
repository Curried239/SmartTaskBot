import streamlit as st
import time
import random
import json
import os

# ----------------- Setup -----------------
st.set_page_config(page_title="SmartTaskBot", page_icon="✨")
TASKS_FILE = "tasks.json"

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

if time.time() - st.session_state['last_reminder_time'] > 60:
    st.sidebar.info(random.choice(reminders))
    st.session_state['last_reminder_time'] = time.time()

# ----------------- Load/Save JSON -----------------
def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

# Initialize session task list
if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()

# ----------------- UI -----------------
st.title("✨ SmartTaskBot v1.5 ✨")
user_name = st.text_input("What's your name?", placeholder="Optional")

if user_name.strip():
    st.subheader(f"Hi {user_name.strip().title()}! Let’s gently plan your day.")
else:
    st.subheader("Let’s gently plan your day.")

mood = st.radio("How are you feeling today?", ["Energetic ⚡", "Neutral ☁", "Tired 💤"])

tasks_input = st.text_area("📝 Enter tasks (comma-separated):", placeholder="e.g., submit report, email client")

# ----------------- Add Tasks -----------------
if st.button("Add to My Day"):
    if tasks_input.strip():
        new_tasks = [task.strip() for task in tasks_input.split(",") if task.strip()]
        for task in new_tasks:
            if not any(t['text'] == task for t in st.session_state.tasks):
                st.session_state.tasks.append({"text": task, "done": False})
        save_tasks(st.session_state.tasks)
        st.success("Tasks added to your day!")
    else:
        st.warning("Please enter at least one task.")

# ----------------- Clear Tasks -----------------
if st.button("Clear My Tasks ❌"):
    st.session_state.tasks.clear()
    save_tasks([])
    st.success("Your task list has been cleared!")

# ----------------- Prioritize Button -----------------
# ----------------- Prioritize Button -----------------
if st.button("Prioritize My Day 💡"):
    input_tasks = [task.strip() for task in tasks_input.split(",") if task.strip()]
    use_input = bool(input_tasks)

    if not use_input and not st.session_state.tasks:
        st.warning("Please enter tasks or use 'Add to My Day' first.")
    else:
        st.markdown("### ✅ Your Prioritized Tasks:")

        priority_keywords = ["urgent", "important", "asap", "today", "now", "deadline"]
        tiring_words = ["report", "presentation", "fix", "debug", "analyze", "meeting"]

        def get_score(text):
            score = 0
            lower = text.lower()
            for word in priority_keywords:
                if word in lower:
                    score += 2
            if len(lower) > 25:
                score += 1
            return score

        def is_tiring(text):
            lower = text.lower()
            return any(word in lower for word in priority_keywords + tiring_words)

        # Build task list: use input OR fallback to saved session tasks
        if use_input:
            task_list = [{"text": t, "done": False} for t in input_tasks]
        else:
            task_list = [t for t in st.session_state.tasks if not t["done"]]

        # Filter and sort
        filtered_tasks = []
        for task in task_list:
            if mood == "Tired 💤" and is_tiring(task["text"]):
                continue
            if mood == "Neutral ☁" and get_score(task["text"]) > 2:
                continue
            filtered_tasks.append((task["text"], get_score(task["text"])))

        sorted_tasks = sorted(filtered_tasks, key=lambda x: x[1], reverse=True)

        if sorted_tasks:
            for i, (task, score) in enumerate(sorted_tasks, start=1):
                emoji = "🔥" if score > 2 else "✅"
                st.write(f"{i}.** {task} {emoji}")
        else:
            st.info("No tasks matched your current energy level.")

# ----------------- Mark as Done -----------------
if st.session_state.tasks:
    st.markdown("### ☑ Mark Your Completed Tasks")

    for i, task in enumerate(st.session_state.tasks):
        new_status = st.checkbox(task["text"], value=task["done"], key=f"task_{i}")
        st.session_state.tasks[i]["done"] = new_status

    save_tasks(st.session_state.tasks)
