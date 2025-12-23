import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config("NC Work Management System", layout="wide")

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

# ---------------- SESSION STATE ----------------
def init_state():
    st.session_state.setdefault("tasks", [])
    st.session_state.setdefault("work_logs", [])
    st.session_state.setdefault("call_logs", [])
    st.session_state.setdefault("worklog_approvals", {})  # (user, month, year)
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
    ["Dashboard", "Tasks", "Daily Work Log", "Call Log", "Monthly Approval"]
)

# =====================================================
# DASHBOARD
# =====================================================
if menu == "Dashboard":
    st.title(f"📊 Dashboard – {user}")
    today = date.today()

    if is_nc:
        df = pd.DataFrame(st.session_state.tasks)
        if not df.empty:
            df["Overdue"] = df.apply(
                lambda x: x["end_date"] < today and x["status"] not in ["Done", "Closed"],
                axis=1
            )
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Tasks", len(df))
            col2.metric("Completed", len(df[df["status"].isin(["Done","Closed"])]))
            col3.metric("Spilling Tasks", len(df[df["Overdue"]]))
            st.dataframe(df)

    else:
        my_tasks = [t for t in st.session_state.tasks if t["assigned_to"] == user]
        st.metric("My Tasks", len(my_tasks))

# =====================================================
# TASKS
# =====================================================
elif menu == "Tasks":
    st.title("📝 Task Management")

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

    for t in st.session_state.tasks:
        if t["assigned_to"] == user or (is_nc and user in t["reporters"]):
            with st.expander(f"#{t['id']} | {t['title']} | {t['status']}"):
                st.write(t["description"])
                if t["assigned_to"] == user or is_nc:
                    t["status"] = st.selectbox(
                        "Status",
                        ["To Do","Running","Done","Closed"],
                        index=["To Do","Running","Done","Closed"].index(t["status"]),
                        key=f"s{t['id']}"
                    )

# =====================================================
# DAILY WORK LOG
# =====================================================
elif menu == "Daily Work Log":
    st.title("🗓️ Daily Work Log")

    my_tasks = [t for t in st.session_state.tasks if t["assigned_to"] == user]

    if not my_tasks:
        st.info("No assigned tasks")
    else:
        month_key = (user, date.today().month, date.today().year)
        locked = st.session_state.worklog_approvals.get(month_key, False)

        if locked:
            st.warning("This month is approved. Logs are locked.")
        else:
            task_map = {f"{t['id']} - {t['title']}": t["id"] for t in my_tasks}
            task_sel = st.selectbox("Task", list(task_map.keys()))
            update_type = st.selectbox(
                "Update Type",
                ["Call","Meeting","MOM","Documentation","Follow-up","Other"]
            )
            desc = st.text_area("Work Description")

            if st.button("Log Work"):
                st.session_state.work_logs.append({
                    "date": date.today(),
                    "user": user,
                    "task": task_sel,
                    "update_type": update_type,
                    "description": desc
                })
                st.success("Work logged")

# =====================================================
# CALL LOG (MANAGEMENT ONLY)
# =====================================================
elif menu == "Call Log":
    st.title("📞 Call Log")

    if is_nc:
        st.info("Monitoring only")
        if st.session_state.call_logs:
            st.dataframe(pd.DataFrame(st.session_state.call_logs))
        else:
            st.info("No call logs")

    else:
        person = st.text_input("Person Called")
        call_type = st.selectbox("Call Type", ["SC","DC","Lead","Others"])
        state = st.selectbox("State", INDIAN_STATES)
        other_state = ""
        if state == "Other":
            other_state = st.text_input("Specify State")
        desc = st.text_area("Call Description")

        task_link = st.selectbox(
            "Related Task",
            ["None"] + [f"{t['id']} - {t['title']}" for t in st.session_state.tasks if t["assigned_to"] == user]
        )

        if st.button("Log Call"):
            st.session_state.call_logs.append({
                "date": date.today(),
                "user": user,
                "person_called": person,
                "call_type": call_type,
                "state": other_state if state == "Other" else state,
                "description": desc,
                "task": task_link
            })
            st.success("Call logged")

# =====================================================
# MONTHLY WORK LOG APPROVAL (NC ONLY)
# =====================================================
elif menu == "Monthly Approval":
    st.title("✅ Monthly Work Log Approval")

    if not is_nc:
        st.info("Only NCs can approve")
    else:
        sel_user = st.selectbox("Management User", MANAGEMENT)
        sel_month = st.selectbox("Month", range(1,13))
        sel_year = st.selectbox("Year", [date.today().year, date.today().year-1])

        logs = [
            l for l in st.session_state.work_logs
            if l["user"] == sel_user and
               l["date"].month == sel_month and
               l["date"].year == sel_year
        ]

        if logs:
            st.dataframe(pd.DataFrame(logs))
            key = (sel_user, sel_month, sel_year)
            if not st.session_state.worklog_approvals.get(key, False):
                if st.button("Approve Month"):
                    st.session_state.worklog_approvals[key] = True
                    st.success("Month approved")
            else:
                st.success("Already approved")
        else:
            st.info("No logs for selected period")
