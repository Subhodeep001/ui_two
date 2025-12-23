import streamlit as st
import pandas as pd
from datetime import date, timedelta

st.set_page_config("NC Work Management System", layout="wide")

# ---------------- USERS ----------------
NCs = ["Rishabh", "Subho", "Kunal"]
MANAGEMENT = ["Akshay", "Narendra", "Vatsal"]
ALL_USERS = NCs + MANAGEMENT

# ---------------- SESSION STATE ----------------
def init_state():
    st.session_state.setdefault("tasks", [])
    st.session_state.setdefault("work_logs", [])
    st.session_state.setdefault("leaves", [])  # approved leaves only

init_state()

# ---------------- LOGIN ----------------
st.sidebar.title("🔐 Login")
user = st.sidebar.selectbox("Select User", ALL_USERS)
is_nc = user in NCs

menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Tasks", "Daily Work Log"]
)

today = date.today()
editable_from = today - timedelta(days=6)

# =====================================================
# DASHBOARD
# =====================================================
if menu == "Dashboard":
    st.title(f"📊 Dashboard – {user}")

    if is_nc:
        st.subheader("📋 All Work Logs")
        if st.session_state.work_logs:
            st.dataframe(pd.DataFrame(st.session_state.work_logs))
        else:
            st.info("No work logs yet")

    else:
        my_logs = [l for l in st.session_state.work_logs if l["user"] == user]
        if my_logs:
            st.dataframe(pd.DataFrame(my_logs))
        else:
            st.info("No work logs yet")

# =====================================================
# TASKS
# =====================================================
elif menu == "Tasks":
    st.title("📝 Tasks")

    # Create task
    title = st.text_input("Task Title")
    desc = st.text_area("Task Description")
    end_date = st.date_input("End Date")

    if is_nc:
        assigned_to = st.selectbox("Assign To", MANAGEMENT)
    else:
        assigned_to = user

    if st.button("Create Task"):
        st.session_state.tasks.append({
            "id": len(st.session_state.tasks) + 1,
            "title": title,
            "description": desc,
            "assigned_to": assigned_to,
            "end_date": end_date
        })
        st.success("Task Created")

    st.divider()

    for t in st.session_state.tasks:
        if t["assigned_to"] == user or is_nc:
            with st.expander(f"#{t['id']} | {t['title']} | {t['assigned_to']}"):
                st.write(t["description"])
                st.write(f"Due: {t['end_date']}")

# =====================================================
# DAILY WORK LOG
# =====================================================
elif menu == "Daily Work Log":
    st.title("🗓️ Daily Work Log")

    if is_nc:
        st.info("NCs can only view logs")
        if st.session_state.work_logs:
            st.dataframe(pd.DataFrame(st.session_state.work_logs))
        else:
            st.info("No logs yet")

    else:
        log_date = st.date_input(
            "Log Date",
            today,
            min_value=editable_from,
            max_value=today
        )

        # Check leave
        on_leave = any(
            l["user"] == user and l["date"] == log_date
            for l in st.session_state.leaves
        )

        my_tasks = [t for t in st.session_state.tasks if t["assigned_to"] == user]

        if on_leave:
            st.warning("You are on leave. No work done will be recorded.")
            if not any(
                wl["user"] == user and wl["date"] == log_date
                for wl in st.session_state.work_logs
            ):
                st.session_state.work_logs.append({
                    "date": log_date,
                    "user": user,
                    "task": None,
                    "description": "No work done – On Leave"
                })
                st.success("Leave log recorded")

        elif not my_tasks:
            st.info("No assigned tasks")

        else:
            task_map = {f"{t['id']} - {t['title']}": t["id"] for t in my_tasks}
            selected_task = st.selectbox("Task", list(task_map.keys()))
            work_desc = st.text_area("What did you do today?")

            existing = next(
                (wl for wl in st.session_state.work_logs
                 if wl["user"] == user and wl["date"] == log_date),
                None
            )

            if existing:
                st.info("Updating existing log")

            if st.button("Save Log"):
                if existing:
                    existing["task"] = selected_task
                    existing["description"] = work_desc
                else:
                    st.session_state.work_logs.append({
                        "date": log_date,
                        "user": user,
                        "task": selected_task,
                        "description": work_desc
                    })
                st.success("Work log saved")
