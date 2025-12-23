import streamlit as st
import pandas as pd
from datetime import date, timedelta

st.set_page_config("NC Operations Tracker", layout="wide")

# ---------------- USERS ----------------
NCs = ["Rishabh", "Subho", "Kunal"]
MANAGEMENT = ["Akshay", "Narendra", "Vatsal"]
ALL_USERS = NCs + MANAGEMENT

LEAVE_TYPES = {"CL": 15, "SL": 7, "COURSE": 7}

INDIAN_STATES = [
    "Andhra Pradesh","Assam","Bihar","Chhattisgarh","Delhi","Goa","Gujarat",
    "Haryana","Himachal Pradesh","Jharkhand","Karnataka","Kerala","Madhya Pradesh",
    "Maharashtra","Odisha","Punjab","Rajasthan","Tamil Nadu","Telangana",
    "Uttar Pradesh","Uttarakhand","West Bengal","Other"
]

MEETING_SCOPE = ["Pan India", "State-wise", "With DCs", "With NCs"]

# ---------------- SESSION STATE ----------------
def init_state():
    st.session_state.setdefault("tasks", [])
    st.session_state.setdefault("task_logs", [])
    st.session_state.setdefault("call_logs", [])
    st.session_state.setdefault("meeting_logs", [])
    st.session_state.setdefault("leave_requests", [])
    st.session_state.setdefault(
        "leave_balance",
        {u: LEAVE_TYPES.copy() for u in MANAGEMENT}
    )

init_state()

# ---------------- LOGIN ----------------
st.sidebar.title("🔐 Login")
user = st.sidebar.selectbox("User", ALL_USERS)
is_nc = user in NCs

menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Tasks", "Daily Logs", "Leave"]
)

today = date.today()
editable_from = today - timedelta(days=6)

# =====================================================
# DASHBOARD
# =====================================================
if menu == "Dashboard":
    st.title(f"📊 Dashboard – {user}")

    if is_nc:
        sel_date = st.date_input("Select Date", today)

        def show(title, data):
            if data:
                st.subheader(title)
                st.dataframe(pd.DataFrame(data))

        show("📝 Task Logs", [l for l in st.session_state.task_logs if l["date"] == sel_date])
        show("📞 Call Logs", [l for l in st.session_state.call_logs if l["date"] == sel_date])
        show("🧑‍🤝‍🧑 Meeting Logs", [l for l in st.session_state.meeting_logs if l["date"] == sel_date])

    else:
        my_logs = (
            st.session_state.task_logs +
            st.session_state.call_logs +
            st.session_state.meeting_logs
        )
        my_logs = [l for l in my_logs if l["user"] == user]
        if my_logs:
            st.dataframe(pd.DataFrame(my_logs))
        else:
            st.info("No activity logged yet")

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
# DAILY LOGS
# =====================================================
elif menu == "Daily Logs":
    st.title("🗓️ Daily Logs")

    if is_nc:
        st.info("NCs can monitor only")
        st.stop()

    log_date = st.date_input(
        "Log Date",
        today,
        min_value=editable_from,
        max_value=today
    )

    # Leave check
    approved_leave = any(
        l["user"] == user and l["date"] == log_date and l["status"] == "Approved"
        for l in st.session_state.leave_requests
    )

    if approved_leave:
        st.warning("On approved leave. No work done.")
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
    task_opts = ["None"] + [f"{t['id']} - {t['title']}" for t in my_tasks]

    if log_type == "Task Work":
        task = st.selectbox("Task", task_opts[1:])
        desc = st.text_area("Work Done")

        if st.button("Save Task Log"):
            st.session_state.task_logs.append({
                "date": log_date,
                "user": user,
                "task": task,
                "description": desc
            })
            st.success("Task work logged")

    elif log_type == "Call":
        person = st.text_input("Person Called")
        ctype = st.selectbox("Call Type", ["SC","DC","Lead","Others"])
        state = st.selectbox("State", INDIAN_STATES)
        final_state = st.text_input("Specify State") if state == "Other" else state
        desc = st.text_area("Call Description")
        task = st.selectbox("Related Task", task_opts)

        if st.button("Save Call Log"):
            st.session_state.call_logs.append({
                "date": log_date,
                "user": user,
                "person_called": person,
                "call_type": ctype,
                "state": final_state,
                "description": desc,
                "task": task
            })
            st.success("Call logged")

    elif log_type == "Meeting":
        scope = st.selectbox("Meeting Scope", MEETING_SCOPE)
        mode = st.selectbox("Mode", ["Online","Offline"])
        participants = st.text_area("Participants")
        mom = st.text_area("MOM / Outcome")
        task = st.selectbox("Related Task", task_opts)

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

# =====================================================
# LEAVE
# =====================================================
elif menu == "Leave":
    st.title("🌴 Leave Management")

    if not is_nc:
        st.subheader("📊 Leave Balance")
        st.json(st.session_state.leave_balance[user])

        ltype = st.selectbox("Leave Type", list(LEAVE_TYPES.keys()))
        ldate = st.date_input("Leave Date")
        reason = st.text_input("Reason")

        if st.button("Apply Leave"):
            if st.session_state.leave_balance[user][ltype] > 0:
                st.session_state.leave_requests.append({
                    "user": user,
                    "type": ltype,
                    "date": ldate,
                    "reason": reason,
                    "status": "Pending"
                })
                st.success("Leave applied")
            else:
                st.error("No balance left")

    else:
        st.subheader("✅ Leave Approvals")
        for l in st.session_state.leave_requests:
            if l["status"] == "Pending":
                with st.expander(f"{l['user']} | {l['type']} | {l['date']}"):
                    st.write(l["reason"])
                    if st.button("Approve", key=f"{l['user']}{l['date']}"):
                        l["status"] = "Approved"
                        st.session_state.leave_balance[l["user"]][l["type"]] -= 1
                        st.success("Approved")
