```python
import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
import time

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Smart Home Security Monitor", layout="wide")

# ------------------ ADVANCED CYBER UI ------------------
st.markdown("""
<style>

/* Background */
body {
    background: linear-gradient(135deg, #0b0f19, #05070d);
}

/* Title */
.cyber-title {
    font-size: 42px;
    font-weight: bold;
    text-align: center;
    color: #00ffc6;
    text-shadow: 0 0 20px #00ffc6;
    animation: glow 2s infinite alternate;
}

@keyframes glow {
    from { text-shadow: 0 0 10px #00ffc6; }
    to { text-shadow: 0 0 25px #00ffc6; }
}

/* Glass Card */
.card {
    background: rgba(18, 24, 38, 0.7);
    backdrop-filter: blur(12px);
    padding: 20px;
    border-radius: 15px;
    border: 1px solid rgba(0,255,204,0.2);
    box-shadow: 0 0 20px rgba(0,255,204,0.1);
    transition: 0.3s;
}

.card:hover {
    transform: scale(1.02);
    box-shadow: 0 0 30px rgba(0,255,204,0.4);
}

/* Alerts */
.alert-red {
    color: #ff4b4b;
    font-weight: bold;
    font-size: 18px;
    text-shadow: 0 0 10px #ff4b4b;
}

.alert-green {
    color: #00ff99;
    font-weight: bold;
    font-size: 18px;
}

/* Metrics */
[data-testid="stMetric"] {
    background: rgba(18,24,38,0.6);
    border-radius: 12px;
    padding: 10px;
    box-shadow: 0 0 10px rgba(0,255,204,0.2);
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #00ffc6, #00aaff);
    color: black;
    font-weight: bold;
    border-radius: 8px;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: scale(1.05);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #05070d;
    border-right: 1px solid rgba(0,255,204,0.2);
}

</style>
""", unsafe_allow_html=True)

# ------------------ SESSION STATE ------------------
if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0

if "alerts_list" not in st.session_state:
    st.session_state.alerts_list = []

# ------------------ ACCESS CONTROL ------------------
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

    return pd.DataFrame(data).sort_values(by="Time", ascending=False)

# ------------------ ANALYSIS ------------------
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

# ------------------ SIDEBAR ------------------
st.sidebar.title("⚙️ Control Panel")

alarm_mode = st.sidebar.toggle("🔔 Alarm System", value=True)
auto_refresh = st.sidebar.toggle("🔄 Live Monitoring", value=True)

st.sidebar.markdown("---")
st.sidebar.info("Smart AI Security Dashboard")

# ------------------ HEADER ------------------
st.markdown('<div class="cyber-title">🏠 Smart Home Security Monitor</div>', unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; margin-bottom:10px;">
⚡ Real-time Monitoring | 🧠 AI Detection | 🔐 Secure Access
</div>
""", unsafe_allow_html=True)

# ------------------ DATA ------------------
df = generate_data()
df["Status"] = df.apply(analyze, axis=1)
df["Risk Level"] = df["Status"].apply(get_risk)

alerts = df[df["Status"] != "✅ Normal"]

# ------------------ SYSTEM STATUS ------------------
st.markdown("### 🛡️ System Status")

if len(alerts) > 0:
    st.markdown("<p class='alert-red'>🚨 SYSTEM UNDER THREAT</p>", unsafe_allow_html=True)
else:
    st.markdown("<p class='alert-green'>✅ SYSTEM SECURE</p>", unsafe_allow_html=True)

# ------------------ STYLE FUNCTION ------------------
def style_risk(val):
    if "High" in val:
        return "color: red; font-weight: bold"
    elif "Medium" in val:
        return "color: orange; font-weight: bold"
    else:
        return "color: lightgreen; font-weight: bold"

# ------------------ DASHBOARD ------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📊 Sensor Data")

    show_df = df.copy()
    show_df["Time"] = show_df["Time"].dt.strftime("%Y-%m-%d %H:%M:%S")

    st.dataframe(show_df.style.applymap(style_risk, subset=["Risk Level"]), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🚨 Alerts Panel")

    if alerts.empty:
        st.success("No suspicious activity")
    else:
        st.error("Threats detected!")

        show_alerts = alerts.copy()
        show_alerts["Time"] = show_alerts["Time"].dt.strftime("%Y-%m-%d %H:%M:%S")

        st.dataframe(show_alerts, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ METRICS ------------------
st.markdown("### 📊 Security Metrics")

m1, m2, m3 = st.columns(3)

with m1:
    st.metric("📡 Total Events", len(df))

with m2:
    st.metric("🚨 Alerts", len(alerts))

with m3:
    st.metric("🔐 Failed Attempts", st.session_state.failed_attempts)

# ------------------ CHARTS ------------------
st.markdown("### 📈 Activity Insights")

chart_df = df.copy()
chart_df["Hour"] = chart_df["Time"].dt.hour

st.line_chart(chart_df.groupby("Hour")["Motion"].sum())
st.bar_chart(chart_df["Location"].value_counts())

# ------------------ ACCESS PANEL ------------------
st.markdown("### 🔐 Access Control Panel")

user_code = st.text_input("Enter Secure Access Code", type="password")

if st.button("Authorize Access"):
    result = check_access(user_code)

    if "Intruder" in result or "LOCKED" in result:
        if alarm_mode:
            st.error(result)
            st.warning("🔊 SECURITY ALARM ACTIVATED")
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
st.markdown("🔒 Smart Security System | Hackathon Ready 🚀")
```
