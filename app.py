import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
import time

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Security Control Panel", layout="wide")

# ------------------ DARK THEME ------------------
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: white;
}
h1 {
    color: red;
}
</style>
""", unsafe_allow_html=True)

# ------------------ SESSION STATE ------------------
if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0

if "alerts_list" not in st.session_state:
    st.session_state.alerts_list = []

# ------------------ ACCESS CODE ------------------
CORRECT_CODE = "1234"

def check_access(input_code):
    if st.session_state.failed_attempts >= 3:
        return "⛔ SYSTEM LOCKED! Too many failed attempts."

    if input_code == CORRECT_CODE:
        st.session_state.failed_attempts = 0
        return "✅ Access Granted"
    else:
        st.session_state.failed_attempts += 1
        msg = f"🚨 Intruder! Attempts: {st.session_state.failed_attempts}/3"
        st.session_state.alerts_list.append(msg)
        return msg

# ------------------ DATA GENERATION ------------------
def generate_data():
    data = []
    now = datetime.now()

    locations = ["Entrance", "Living Room", "Bedroom", "Garage"]

    for _ in range(40):
        mins = random.randint(0, 1440)
        t = now - timedelta(minutes=mins)

        data.append({
            "Time": t,
            "Motion": random.choice([0, 1]),
            "Door": random.choice(["Open", "Closed"]),
            "Location": random.choice(locations)
        })

    df = pd.DataFrame(data).sort_values(by="Time", ascending=False)
    return df

# ------------------ RISK ANALYSIS ------------------
def analyze(row):
    hour = row["Time"].hour

    if row["Motion"] == 1 and (1 <= hour <= 5):
        return "⚠️ Late Night Movement"

    if row["Motion"] == 1 and row["Door"] == "Closed":
        return "⚠️ Motion Without Door Open"

    return "✅ Normal"

def get_risk(status):
    if "Late Night" in status:
        return "🟡 Medium"
    if "Motion Without" in status:
        return "🔴 High"
    return "🟢 Low"

# ------------------ HEADER ------------------
st.markdown("<h1>🔐 SECURITY CONTROL PANEL</h1>", unsafe_allow_html=True)

alarm_mode = st.toggle("🔔 Alarm System ON/OFF", value=True)
auto_refresh = st.toggle("🔄 Live Monitoring", value=True)

# ------------------ DATA ------------------
df = generate_data()
df["Status"] = df.apply(analyze, axis=1)
df["Risk Level"] = df["Status"].apply(get_risk)

alerts = df[df["Status"] != "✅ Normal"]

# ------------------ SYSTEM STATUS ------------------
if len(alerts) > 0:
    st.error("🚨 SYSTEM UNDER THREAT")
else:
    st.success("✅ SYSTEM SECURE")

# ------------------ DASHBOARD ------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Sensor Data")
    show_df = df.copy()
    show_df["Time"] = show_df["Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    st.dataframe(show_df, use_container_width=True)

with col2:
    st.subheader("🚨 Alerts Panel")

    if alerts.empty:
        st.success("No suspicious activity")
    else:
        st.error("Threats detected!")

        show_alerts = alerts.copy()
        show_alerts["Time"] = show_alerts["Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
        st.dataframe(show_alerts, use_container_width=True)

# ------------------ METRICS ------------------
st.markdown("### 📈 Security Metrics")

m1, m2, m3 = st.columns(3)
m1.metric("Total Events", len(df))
m2.metric("Alerts", len(alerts))
m3.metric("Failed Attempts", st.session_state.failed_attempts)

# ------------------ CHARTS ------------------
st.markdown("### 📊 Activity Insights")

chart_df = df.copy()
chart_df["Hour"] = chart_df["Time"].dt.hour

motion_chart = chart_df.groupby("Hour")["Motion"].sum()
st.line_chart(motion_chart)

location_chart = chart_df["Location"].value_counts()
st.bar_chart(location_chart)

# ------------------ ACCESS SYSTEM ------------------
st.markdown("### 🔐 Access Control")

user_code = st.text_input("Enter Access Code", type="password")

if st.button("Unlock Door"):
    result = check_access(user_code)

    if "Intruder" in result or "LOCKED" in result:
        if alarm_mode:
            st.error(result)
            st.warning("🔊 ALARM TRIGGERED!")
        else:
            st.warning(result)
    else:
        st.success(result)

# ------------------ SECURITY LOG ------------------
if st.session_state.alerts_list:
    st.markdown("### 🚨 Security Log")
    for alert in st.session_state.alerts_list:
        st.write(alert)

# ------------------ AUTO REFRESH ------------------
if auto_refresh:
    time.sleep(5)
    st.rerun()

# ------------------ FOOTER ------------------
st.markdown("---")
st.markdown("🔒 Smart Security System | Hackathon Project | Python + Streamlit")
