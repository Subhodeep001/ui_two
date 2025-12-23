import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config("NC Task & Leave System", layout="wide")

# ---------------- USERS ----------------
NCs = ["Rishabh", "Subho", "Kunal"]
MANAGEMENT = ["Akshay", "Narendra", "Vatsal"]
ALL_USERS = NCs + MANAGEMENT

# ---------------- SESSION STATE ----------------
def init_state():
    st.session_state.setdefault("tasks", [])
    st.session_state.setdefault("work_logs", [])
    st.session_state.setdefault("leaves", [])
    st.session_state.setdefault(
        "leave_balance",
        {u: {"CL": 15, "SL": 7, "COURSE": 7} for u in MANAGEMENT}
    )

init_state()

# ---------------- LOGIN ----------------
st.sidebar.title("🔐 Login")
user = st.sidebar.selectbox("User", ALL_USERS)
is_nc = user in NCs
menu = st.sidebar.radio("Menu", ["Dashboard", "Tasks", "Leave", "Timesheet"])

# =====================================================
# DASHBOARD
# =====================================================
if menu == "Dashboard":
    st.title(f"📊 Dashboard – {user}")

    if is_nc:
        st.subheader("📌 Pending Tasks by User")
        pending = [t for t in st.session_state.tasks if t["status"] != "Done"]
        if pending:
            st.dataframe(pd.DataFrame(pending))
        else:
            st.success("No pending tasks 🎉")

    else:
        my_tasks = [t for t in st.session_state.tasks if t["assigned_to"] == user]
        st.metric("My Tasks", len(my_tasks))
        st.metric("Running", len([t for t in my_tasks if t["status"] == "Running"]))
        st.metric("Completed", len([t for t in my_tasks if t["status"] == "Done"]))

# =====================================================
# TASKS
# =====================================================
elif menu == "Tasks":
    st.title("📝 Task Management")

    st.subheader("➕ Create Task")
    title = st.text_input("Task Title")
    desc = st.text_area("Task Description")

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
            "created_by": user,
            "status": "To Do"
        })
        st.success("Task Created")

    st.divider()
    st.subheader("📋 Tasks View")

    for t in st.session_state.tasks:
        if is_nc or t["assigned_to"] == user:
            with st.expander(f"#{t['id']} {t['title']} ({t['assigned_to']})"):
                st.write(t["description"])
                t["status"] = st.selectbox(
                    "Status",
                    ["To Do", "Running", "Done"],
                    index=["To Do", "Running", "Done"].index(t["status"]),
                    key=f"s{t['id']}"
                )

                if not is_nc and t["assigned_to"] == user:
                    work = st.text_area("Today's Work", key=f"w{t['id']}")
                    if st.button("Add Work Log", key=f"b{t['id']}"):
                        st.session_state.work_logs.append({
                            "date": date.today(),
                            "user": user,
                            "task_id": t["id"],
                            "work": work
                        })
                        st.success("Work logged")

# =====================================================
# LEAVE
# =====================================================
elif menu == "Leave":
    st.title("🌴 Leave Management")

    if not is_nc:
        bal = st.session_state.leave_balance[user]
        st.subheader("📊 Leave Balance")
        st.json(bal)

        ltype = st.selectbox("Leave Type", ["CL", "SL", "COURSE"])
        ldate = st.date_input("Leave Date")
        reason = st.text_input("Reason")

        if st.button("Apply Leave"):
            if bal[ltype] > 0:
                st.session_state.leaves.append({
                    "user": user,
                    "type": ltype,
                    "date": ldate,
                    "reason": reason,
                    "status": "Pending"
                })
                st.success("Leave Applied")
            else:
                st.error("No balance left")

    if is_nc:
        st.subheader("✅ Leave Approvals")
        for l in st.session_state.leaves:
            if l["status"] == "Pending":
                with st.expander(f"{l['user']} – {l['type']} on {l['date']}"):
                    st.write(l["reason"])
                    if st.button("Approve", key=f"a{l['user']}{l['date']}"):
                        l["status"] = "Approved"
                        st.session_state.leave_balance[l["user"]][l["type"]] -= 1
                        st.success("Approved")

# =====================================================
# TIMESHEET
# =====================================================
elif menu == "Timesheet":
    st.title("🧾 Timesheet")

    logs = [l for l in st.session_state.work_logs if l["user"] == user]

    if logs:
        st.dataframe(pd.DataFrame(logs))
    else:
        st.info("No work logs yet")

    if is_nc:
        st.subheader("👀 Team Timesheets")
        if st.session_state.work_logs:
            st.dataframe(pd.DataFrame(st.session_state.work_logs))
        else:
            st.info("No logs submitted")
