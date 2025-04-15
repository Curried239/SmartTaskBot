import streamlit as st
import time
import random

# -------------- Setup --------------
st.set_page_config(page_title="SmartTaskBot", page_icon="✨")

# -------------- Gentle Reminders --------------
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

# -------------- Session State --------------
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "cleared" not in st.session_state:
    st.session_state.cleared = False

# -------------- UI --------------
st.title("✨ SmartTaskBot ✨")
st.subheader("Hi Anicka! Let’s gently plan your day.")

mood = st.radio("How are you feeling today?", ["Energetic ⚡", "Neutral ☁", "Tired 💤"])

# Task Input
tasks_input = st.text_area("📝 Enter your tasks (separated by commas):",
                           placeholder="e.g., submit report, reply to email, call mom")

# Add to My Day (optional)
if st.button("Add to My Day"):
    if tasks_input.strip():
        new_tasks = [task.strip() for task in tasks_input.split(",") if task.strip()]
        for task in new_tasks:
            if task not in st.session_state.tasks:
                st.session_state.tasks.append(task)
        st.success("Tasks added to your saved list!")
    else:
        st.warning("Please enter a task.")

# Clear Tasks
if st.button("Clear My Tasks ❌"):
    st.session_state.tasks.clear()
    st.success("Your task list has been cleared!")

# Prioritize Button (works independently)
if st.button("Prioritize My Day 💡"):
    all_input_tasks = [task.strip() for task in tasks_input.split(",") if task.strip()]

    if not all_input_tasks:
        st.warning("Please enter some tasks to prioritize.")
    else:
        st.markdown("### ✅ Your Prioritized Tasks:")

        priority_keywords = ["urgent", "important", "asap", "today", "now", "deadline"]
        tiring_words = ["report", "presentation", "fix", "debug", "analyze", "meeting"]

        def get_score(task):
            score = 0
            task_lower = task.lower()
            for word in priority_keywords:
                if word in task_lower:
                    score += 2
            if len(task_lower) > 25:
                score += 1
            return score

        def is_tiring(task):
            task_lower = task.lower()
            return any(word in task_lower for word in priority_keywords + tiring_words)

        scored_tasks = [(task, get_score(task)) for task in all_input_tasks]

        # Mood filtering
        if mood == "Tired 💤":
            filtered_tasks = [(t, s) for t, s in scored_tasks if not is_tiring(t)]
        elif mood == "Neutral ☁":
            filtered_tasks = [(t, s) for t, s in scored_tasks if s <= 2]
        else:  # Energetic ⚡
            filtered_tasks = scored_tasks

        sorted_tasks = sorted(filtered_tasks, key=lambda x: x[1], reverse=True)

        if sorted_tasks:
            for i, (task, score) in enumerate(sorted_tasks, start=1):
                emoji = "🔥" if score > 2 else "✅"
                st.write(f"{i}.** {task} {emoji}")
        else:
            st.info("No low-effort tasks found for your current energy level.")
