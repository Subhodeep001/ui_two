import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config("NC Work Management System", layout="wide")

# ---------------- USERS ----------------
NCs = ["Rishabh", "Subho", "Kunal"]
MANAGEMENT = ["Akshay", "Narendra", "Vatsal"]
ALL_USERS = NCs + MANAGEMENT

# ---------------- SESSION STATE ----------------
def init_state():
    st.session_state.setdefault("tasks", [])
    st.session_state.setdefault("work_logs", [])
    st.session_state.setdefault("call_logs", [])
    st.session_state.setdefault(
        "leave_balance",
        {u: {"CL": 15, "SL": 7, "COURSE": 7} for u in MANAGEMENT}
    )

init_state()

# ---------------- LOGIN ----------------
st.sidebar.title("🔐 Login")
user = st.sidebar.selectbox("Select User", ALL_USERS)
is_nc = user in NCs

menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Tasks", "Daily Work Log", "Call Log"]
)

# =====================================================
# DASHBOARD
# =====================================================
if menu == "Dashboard":
    st.title(f"📊 Dashboard – {user}")

    today = date.today()

    if is_nc:
        st.subheader("📌 Task Overview")

        if st.session_state.tasks:
            df = pd.DataFrame(st.session_state.tasks)
            df["Overdue"] = df.apply(
                lambda x: x["end_date"] < today and x["status"] not in ["Done", "Closed"],
                axis=1
            )

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Tasks", len(df))
            col2.metric("Completed", len(df[df["status"].isin(["Done", "Closed"])]))
            col3.metric("Spilling Tasks", len(df[df["Overdue"]]))

            st.dataframe(df)

        st.divider()
        st.subheader("🗓️ Day-wise Team Activity")

        selected_date = st.date_input("Select Date", today)

        daily_work = [
            w for w in st.session_state.work_logs
            if w["date"] == selected_date
        ]

        daily_calls = [
            c for c in st.session_state.call_logs
            if c["date"] == selected_date
        ]

        if daily_work:
            st.markdown("### 📝 Work Updates")
            st.dataframe(pd.DataFrame(daily_work))

        if daily_calls:
            st.markdown("### 📞 Call Logs")
            st.dataframe(pd.DataFrame(daily_calls))

        if not daily_work and not daily_calls:
            st.info("No activity recorded for this date")

    else:
        my_tasks = [t for t in st.session_state.tasks if t["assigned_to"] == user]
        st.metric("My Tasks", len(my_tasks))
        st.metric(
            "Overdue",
            len([
                t for t in my_tasks
                if t["end_date"] < today and t["status"] not in ["Done", "Closed"]
            ])
        )

# =====================================================
# TASKS
# =====================================================
elif menu == "Tasks":
    st.title("📝 Task Management")

    st.subheader("➕ Create Task")

    title = st.text_input("Task Title")
    desc = st.text_area("Task Description")
    start_date = st.date_input("Start Date", date.today())
    end_date = st.date_input("End Date")

    if is_nc:
        assigned_to = st.selectbox("Assign To", MANAGEMENT)
        reporters = st.multiselect("Task Reporters (NCs)", NCs, default=NCs)
    else:
        assigned_to = user
        reporters = NCs

    if st.button("Create Task"):
        st.session_state.tasks.append({
            "id": len(st.session_state.tasks) + 1,
            "title": title,
            "description": desc,
            "assigned_to": assigned_to,
            "created_by": user,
            "start_date": start_date,
            "end_date": end_date,
            "status": "To Do",
            "reporters": reporters
        })
        st.success("Task Created")

    st.divider()
    st.subheader("📋 Task List")

    for t in st.session_state.tasks:
        can_view = (
            t["assigned_to"] == user or
            (is_nc and user in t["reporters"])
        )

        if can_view:
            with st.expander(
                f"#{t['id']} | {t['title']} | {t['assigned_to']} | "
                f"Due: {t['end_date']} | Status: {t['status']}"
            ):
                st.write(t["description"])

                if t["assigned_to"] == user or is_nc:
                    t["status"] = st.selectbox(
                        "Update Status",
                        ["To Do", "Running", "Done", "Closed"],
                        index=["To Do", "Running", "Done", "Closed"].index(t["status"]),
                        key=f"s{t['id']}"
                    )

# =====================================================
# DAILY WORK LOG (ALL USERS)
# =====================================================
elif menu == "Daily Work Log":
    st.title("🗓️ Daily Work Log")

    my_tasks = [
        t for t in st.session_state.tasks
        if t["assigned_to"] == user
    ]

    if not my_tasks:
        st.info("No assigned tasks")
    else:
        task_map = {f"{t['id']} - {t['title']}": t["id"] for t in my_tasks}
        selected_task = st.selectbox("Task", list(task_map.keys()))
        update_type = st.selectbox(
            "Update Type",
            ["Call", "Meeting", "MOM", "Documentation", "Follow-up", "Other"]
        )
        work_desc = st.text_area("What did you do today?")

        if st.button("Log Work"):
            st.session_state.work_logs.append({
                "date": date.today(),
                "user": user,
                "task_id": task_map[selected_task],
                "task": selected_task,
                "update_type": update_type,
                "description": work_desc
            })
            st.success("Work logged")

# =====================================================
# CALL LOG (MANAGEMENT ONLY)
# =====================================================
elif menu == "Call Log":
    st.title("📞 Call Log")

    if is_nc:
        st.info("Call logs are created by Management. Monitoring only.")

        if st.session_state.call_logs:
            st.dataframe(pd.DataFrame(st.session_state.call_logs))
        else:
            st.info("No call logs yet")

    else:
        name = st.text_input("Person Called")
        call_type = st.selectbox("Call Type", ["SC", "DC", "Lead", "Others"])
        call_desc = st.text_area("Call Description")

        related_task = st.selectbox(
            "Related Task (optional)",
            ["None"] + [
                f"{t['id']} - {t['title']}"
                for t in st.session_state.tasks
                if t["assigned_to"] == user
            ]
        )

        if st.button("Log Call"):
            st.session_state.call_logs.append({
                "date": date.today(),
                "user": user,
                "person_called": name,
                "call_type": call_type,
                "description": call_desc,
                "task": related_task
            })
            st.success("Call logged")
