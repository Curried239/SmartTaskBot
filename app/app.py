import streamlit as st
import time
import random

# -------------- Setup -----------------
st.set_page_config(page_title="SmartTaskBot", page_icon="✨")

# ---------------- Theme Toggle ----------------
theme = st.sidebar.radio("Choose Theme:", ["Light Mode 🌞", "Dark Mode 🌙"])

if theme == "Dark Mode 🌙":
    st.markdown(
        """
        <style>
        html, body, [data-testid="stApp"] {
            background-color: #1e1e1e;
            color: #ffffff;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #2c2c2c;
            color: #ffffff;
        }

        .stSidebar .stMarkdown {
            color: #ffffff;
        }

        /* Text Inputs, Text Area, and Radio Buttons */
        .stTextInput > div > div > input,
        .stTextArea > div > textarea,
        .stRadio > div,
        .stMarkdown {
            color: #ffffff !important;
            background-color: #2c2c2c !important;
        }

        /* Radio Buttons */
        .stRadio label, .stRadio div[role="radiogroup"] > div {
            color: #ffffff !important;
        }

        /* Fix Button Styling */
        .stButton > button {
            background-color: #007BFF;
            color: white !important;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
        }

        .stButton > button:hover {
            background-color: #0056b3;
        }

        /* Fix the Radio Button hover color */
        .stRadio div[role="radiogroup"] > div:hover {
            background-color: #444444 !important;
        }

        /* Fix reminders text */
        .stSidebar .stMarkdown {
            color: #ffffff;
        }

        /* Light/Dark Mode toggle label */
        .stRadio > div {
            color: #ffffff !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <style>
        html, body, [data-testid="stApp"] {
            background-color: #ffffff;
            color: #000000;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #f0f2f6;
            color: #000000;
        }

        .stSidebar .stMarkdown {
            color: #000000;
        }

        /* Text Inputs, Text Area, and Radio Buttons */
        .stTextInput > div > div > input,
        .stTextArea > div > textarea,
        .stRadio > div,
        .stMarkdown {
            color: #000000 !important;
            background-color: #ffffff !important;
        }

        /* Radio Buttons */
        .stRadio label, .stRadio div[role="radiogroup"] > div {
            color: #000000 !important;
        }

        /* Fix Button Styling */
        .stButton > button {
            background-color: #007BFF;
            color: white !important;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
        }

        .stButton > button:hover {
            background-color: #0056b3;
        }

        /* Fix the Radio Button hover color */
        .stRadio div[role="radiogroup"] > div:hover {
            background-color: #d3d3d3 !important;
        }

        /* Fix reminders text */
        .stSidebar .stMarkdown {
            color: #000000;
        }

        /* Light/Dark Mode toggle label */
        .stRadio > div {
            color: #000000 !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

# -------------- Gentle Reminders -----------------
reminders = [
    "Take a deep breath and stretch a little!",
    "Stay hydrated — a glass of water never hurts.",
    "You’re doing amazing. Consider a 5-minute break?",
    "Even small steps count — keep going at your pace.",
    "Don’t forget to smile today. You’re making progress!"
]

if 'last_reminder_time' not in st.session_state:
    st.session_state['last_reminder_time'] = time.time()

if time.time() - st.session_state['last_reminder_time'] > 0:  # Every 1 minute (change to 1800 for 30 mins)
    st.sidebar.info(random.choice(reminders))
    st.session_state['last_reminder_time'] = time.time()

# -------------- UI Title & Mood Check -----------------
st.title("✨ SmartTaskBot ✨")
st.subheader("Hi Anicka! Let's gently plan your day.")

mood = st.radio("How are you feeling today?", ["Energetic ⚡", "Neutral ☁", "Tired 💤"])
st.markdown("---")

# -------------- Task Input -----------------
tasks_input = st.text_area("📝 Enter your tasks (separated by commas):", 
                           placeholder="e.g., submit report, reply to email, call mom")

if st.button("Prioritize My Day 💡"):

    if not tasks_input.strip():
        st.warning("Oops! You didn’t add any tasks. Just take your time.")
    else:
        tasks = [task.strip() for task in tasks_input.split(",") if task.strip()]

        # Basic keyword-based priority boost
        priority_keywords = ["urgent", "important", "asap", "today", "now", "deadline"]
        def get_score(task):
            score = 0
            task_lower = task.lower()
            for word in priority_keywords:
                if word in task_lower:
                    score += 2
            # Boost based on task length as a basic complexity marker
            if len(task_lower) > 25:
                score += 1
            return score

        # Mood influence
        mood_filter = {
            "Energetic ⚡": lambda s: s >= 1,
            "Neutral ☁": lambda s: s >= 0,
            "Tired 💤": lambda s: s <= 2
        }

        # Score, filter and sort tasks
        scored_tasks = [(task, get_score(task)) for task in tasks]
        filtered = list(filter(lambda x: mood_filter[mood](x[1]), scored_tasks))
        sorted_tasks = sorted(filtered, key=lambda x: x[1], reverse=True)

        st.success("Here’s your calm, personalized plan for today:")
        if sorted_tasks:
            for i, (task, score) in enumerate(sorted_tasks, start=1):
                emoji = "🔥" if score > 2 else "✅"
                st.write(f"{i}.** {task} {emoji}")
        else:
            st.info("None of your tasks matched your current mood. Want to try rewording or reselect your mood?")
