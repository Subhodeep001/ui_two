import streamlit as st
import pandas as pd
from datetime import date, timedelta

st.set_page_config("NC Daily Work Tracker", layout="wide")

# ---------------- USERS ----------------
NCs = ["Rishabh", "Subho", "Kunal"]
MANAGEMENT = ["Akshay", "Narendra", "Vatsal"]
ALL_USERS = NCs + MANAGEMENT

INDIAN_STATES = [
    "Andhra Pradesh","Assam","Bihar","Chhattisgarh","Delhi","Goa","Gujarat",
    "Haryana","Himachal Pradesh","Jharkhand","Karnataka","Kerala","Madhya Pradesh",
    "Maharashtra","Odisha","Punjab","Rajasthan","Tamil Nadu","Telangana",
    "Uttar Pradesh","Uttarakhand","West Bengal","Other"
]

MEETING_SCOPE = [
    "Pan India",
    "State-wise",
    "With DCs",
    "With NCs"
]

# ---------------- SESSION STATE ----------------
def init_state():
    st.session_state.setdefault("tasks", [])
    st.session_state.setdefault("task_logs", [])
    st.session_state.setdefault("call_logs", [])
    st.session_state.setdefault("meeting_logs", [])
    st.session_state.setdefault("leaves", [])  # approved leaves only

init_state()

# ---------------- LOGIN ----------------
st.sidebar.title("🔐 Login")
user = st.sidebar.selectbox("User", ALL_USERS)
is_nc = user in NCs

menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Tasks", "Daily Logs"]
)

today = date.today()
editable_from = today - timedelta(days=6)

# =====================================================
# DASHBOARD
# =====================================================
if menu == "Dashboard":
    st.title(f"📊 Dashboard – {user}")

    if is_nc:
        selected_date = st.date_input("Select Date", today)

        task_logs = [l for l in st.session_state.task_logs if l["date"] == selected_date]
        call_logs = [l for l in st.session_state.call_logs if l["date"] == selected_date]
        meeting_logs = [l for l in st.session_state.meeting_logs if l["date"] == selected_date]

        if task_logs:
            st.subheader("📝 Task Work")
            st.dataframe(pd.DataFrame(task_logs))

        if call_logs:
            st.subheader("📞 Calls")
            st.dataframe(pd.DataFrame(call_logs))

        if meeting_logs:
            st.subheader("🧑‍🤝‍🧑 Meetings")
            st.dataframe(pd.DataFrame(meeting_logs))

        if not task_logs and not call_logs and not meeting_logs:
            st.info("No activity for this date")

    else:
        st.subheader("📜 My Activity History")
        logs = (
            st.session_state.task_logs +
            st.session_state.call_logs +
            st.session_state.meeting_logs
        )
        my_logs = [l for l in logs if l["user"] == user]
        if my_logs:
            st.dataframe(pd.DataFrame(my_logs))
        else:
            st.info("No logs yet")

# =====================================================
# TASKS
# =====================================================
elif menu == "Tasks":
    st.title("📝 Tasks")

    title = st.text_input("Task Title")
    desc = st.text_area("Task Description")
    end_date = st.date_input("End Date")

    assigned_to = st.selectbox("Assign To", MANAGEMENT) if is_nc else user

    if st.button("Create Task"):
        st.session_state.tasks.append({
            "id": len(st.session_state.tasks) + 1,
            "title": title,
            "description": desc,
            "assigned_to": assigned_to,
            "end_date": end_date
        })
        st.success("Task created")

    st.divider()

    for t in st.session_state.tasks:
        if t["assigned_to"] == user or is_nc:
            with st.expander(f"#{t['id']} | {t['title']} | {t['assigned_to']}"):
                st.write(t["description"])
                st.write(f"Due: {t['end_date']}")

# =====================================================
# DAILY LOGS (MANAGEMENT ONLY)
# =====================================================
elif menu == "Daily Logs":
    st.title("🗓️ Daily Activity Log")

    if is_nc:
        st.info("NCs can only monitor logs")
        st.stop()

    log_date = st.date_input(
        "Log Date",
        today,
        min_value=editable_from,
        max_value=today
    )

    # Leave handling
    if any(l["user"] == user and l["date"] == log_date for l in st.session_state.leaves):
        st.warning("You are on leave. No work done – On Leave.")
        if not any(
            l["user"] == user and l["date"] == log_date
            for l in st.session_state.task_logs
        ):
            st.session_state.task_logs.append({
                "date": log_date,
                "user": user,
                "task": None,
                "description": "No work done – On Leave"
            })
        st.stop()

    log_type = st.radio("Log Type", ["Task Work", "Call", "Meeting"])

    my_tasks = [t for t in st.session_state.tasks if t["assigned_to"] == user]
    task_options = ["None"] + [f"{t['id']} - {t['title']}" for t in my_tasks]

    # ---------- TASK WORK ----------
    if log_type == "Task Work":
        task = st.selectbox("Task", task_options[1:])
        desc = st.text_area("Work Done Today")

        if st.button("Save Task Log"):
            st.session_state.task_logs.append({
                "date": log_date,
                "user": user,
                "task": task,
                "description": desc
            })
            st.success("Task work logged")

    # ---------- CALL ----------
    elif log_type == "Call":
        person = st.text_input("Person Called")
        call_type = st.selectbox("Call Type", ["SC", "DC", "Lead", "Others"])
        state = st.selectbox("State", INDIAN_STATES)
        final_state = st.text_input("Specify State") if state == "Other" else state
        desc = st.text_area("Call Description")
        task = st.selectbox("Related Task", task_options)

        if st.button("Save Call Log"):
            st.session_state.call_logs.append({
                "date": log_date,
                "user": user,
                "person_called": person,
                "call_type": call_type,
                "state": final_state,
                "description": desc,
                "task": task
            })
            st.success("Call logged")

    # ---------- MEETING ----------
    elif log_type == "Meeting":
        scope = st.selectbox("Meeting Scope", MEETING_SCOPE)
        mode = st.selectbox("Mode", ["Online", "Offline"])
        participants = st.text_area("Participants")
        mom = st.text_area("MOM / Outcome")
        task = st.selectbox("Related Task", task_options)

        if st.button("Save Meeting Log"):
            st.session_state.meeting_logs.append({
                "date": log_date,
                "user": user,
                "scope": scope,
                "mode": mode,
                "participants": participants,
                "mom": mom,
                "task": task
            })
            st.success("Meeting logged")
