import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="NC Task & Leave Tracker", layout="wide")

# -------------------------------
# USERS & ROLES
# -------------------------------
MANAGEMENT = ["Subho", "Kunal", "Rishabh"]
NC_TEAM = ["Akshay", "Narendra", "Vatsal"]
ALL_USERS = MANAGEMENT + NC_TEAM

# -------------------------------
# SESSION STATE INIT
# -------------------------------
if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "work_logs" not in st.session_state:
    st.session_state.work_logs = []

if "leaves" not in st.session_state:
    st.session_state.leaves = []

if "approved_timesheets" not in st.session_state:
    st.session_state.approved_timesheets = []

# -------------------------------
# LOGIN
# -------------------------------
st.sidebar.title("🔐 Login")
current_user = st.sidebar.selectbox("Select User", ALL_USERS)
is_manager = current_user in MANAGEMENT

# -------------------------------
# SIDEBAR NAV
# -------------------------------
menu = st.sidebar.radio("Navigation", ["Dashboard", "Tasks", "Leave", "Timesheet"])

# =====================================================
# DASHBOARD
# =====================================================
if menu == "Dashboard":
    st.title(f"📊 Dashboard – {current_user}")

    user_tasks = [t for t in st.session_state.tasks if t["assigned_to"] == current_user]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tasks", len(user_tasks))
    col2.metric("Running", len([t for t in user_tasks if t["status"] == "Running"]))
    col3.metric("Completed", len([t for t in user_tasks if t["status"] == "Done"]))

    st.subheader("📝 My Tasks")
    if user_tasks:
        st.dataframe(pd.DataFrame(user_tasks))
    else:
        st.info("No tasks assigned")

# =====================================================
# TASKS
# =====================================================
elif menu == "Tasks":
    st.title("📌 Task Management")

    st.subheader("➕ Create Task")

    task_title = st.text_input("Task Title")
    task_desc = st.text_area("Task Description")

    if is_manager:
        assigned_to = st.selectbox("Assign To", NC_TEAM)
    else:
        assigned_to = current_user

    if st.button("Create Task"):
        st.session_state.tasks.append({
            "task_id": len(st.session_state.tasks) + 1,
            "title": task_title,
            "description": task_desc,
            "assigned_to": assigned_to,
            "created_by": current_user,
            "status": "To Do"
        })
        st.success("Task Created")

    st.divider()
    st.subheader("📋 My Assigned Tasks")

    for task in st.session_state.tasks:
        if task["assigned_to"] == current_user:
            with st.expander(f"#{task['task_id']} – {task['title']}"):
                st.write(task["description"])

                new_status = st.selectbox(
                    "Update Status",
                    ["To Do", "Running", "Done"],
                    index=["To Do", "Running", "Done"].index(task["status"]),
                    key=f"status_{task['task_id']}"
                )
                task["status"] = new_status

                st.subheader("🗓️ Daily Work Log")
                work_text = st.text_area(
                    "What did you work on today?",
                    key=f"log_{task['task_id']}"
                )

                if st.button("Add Work Log", key=f"btn_{task['task_id']}"):
                    st.session_state.work_logs.append({
                        "date": date.today(),
                        "user": current_user,
                        "task_id": task["task_id"],
                        "work": work_text
                    })
                    st.success("Work log added")

# =====================================================
# LEAVE TRACKER
# =====================================================
elif menu == "Leave":
    st.title("🌴 Leave Tracker")

    leave_date = st.date_input("Leave Date")
    leave_reason = st.text_input("Reason")

    if st.button("Apply Leave"):
        st.session_state.leaves.append({
            "user": current_user,
            "date": leave_date,
            "reason": leave_reason
        })
        st.success("Leave Applied")

    st.subheader("📅 My Leaves")
    user_leaves = [l for l in st.session_state.leaves if l["user"] == current_user]
    if user_leaves:
        st.dataframe(pd.DataFrame(user_leaves))
    else:
        st.info("No leave records")

# =====================================================
# TIMESHEET
# =====================================================
elif menu == "Timesheet":
    st.title("🧾 Monthly Timesheet")

    user_logs = [l for l in st.session_state.work_logs if l["user"] == current_user]

    if user_logs:
        df = pd.DataFrame(user_logs)
        st.dataframe(df)
    else:
        st.info("No work logs found")

    if current_user in NC_TEAM:
        if st.button("Submit Timesheet for Approval"):
            st.session_state.approved_timesheets.append(current_user)
            st.success("Timesheet submitted")

    if is_manager:
        st.subheader("✅ Approve NC Timesheets")
        for nc in NC_TEAM:
            if nc in st.session_state.approved_timesheets:
                st.success(f"{nc} – Timesheet Submitted")
