import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
import time

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Smart Home Security Monitor", layout="wide")

# ------------------ CYBER UI + ALERT ANIMATION ------------------
st.markdown("""
<style>

/* Base Theme */
body { background-color: #0b0f19; }
.main { background-color: #0b0f19; color: #e0e0e0; }

/* Title */
.cyber-title {
    font-size: 38px;
    font-weight: bold;
    text-align: center;
    color: #00ffcc;
    text-shadow: 0px 0px 15px #00ffcc;
}

/* Cards */
.card {
    background-color: #121826;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0 0 12px rgba(0,255,204,0.2);
    margin-bottom: 10px;
}

/* Flashing red screen */
@keyframes flashRed {
    0% { background-color: #0b0f19; }
    50% { background-color: rgba(255,0,0,0.6); }
    100% { background-color: #0b0f19; }
}

.flash {
    animation: flashRed 1s infinite;
}

/* Siren text animation */
@keyframes blink {
    0% { color: red; }
    50% { color: white; }
    100% { color: red; }
}

.siren {
    font-size: 28px;
    font-weight: bold;
    text-align: center;
    animation: blink 1s infinite;
}

/* Status */
.alert-red { color: #ff4b4b; font-weight: bold; }
.alert-green { color: #00ff99; font-weight: bold; }

</style>
""", unsafe_allow_html=True)

# ------------------ SESSION ------------------
if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0

if "alerts_list" not in st.session_state:
    st.session_state.alerts_list = []

if "intrusion" not in st.session_state:
    st.session_state.intrusion = False

# ------------------ ACCESS ------------------
CORRECT_CODE = "1234"

def check_access(input_code):
    if st.session_state.failed_attempts >= 3:
        st.session_state.intrusion = True
        return "⛔ SYSTEM LOCKED!"

    if input_code == CORRECT_CODE:
        st.session_state.failed_attempts = 0
        st.session_state.intrusion = False
        return "✅ Access Granted"
    else:
        st.session_state.failed_attempts += 1
        st.session_state.intrusion = True
        msg = f"🚨 Intruder! Attempts: {st.session_state.failed_attempts}/3"
        st.session_state.alerts_list.append(msg)
        return msg

# ------------------ DATA ------------------
def generate_data():
    data = []
    now = datetime.now()
    locations = ["Entrance", "Living Room", "Bedroom", "Garage"]

    for _ in range(40):
        t = now - timedelta(minutes=random.randint(0, 1440))
        data.append({
            "Time": t,
            "Motion": random.choice([0, 1]),
            "Door": random.choice(["Open", "Closed"]),
            "Location": random.choice(locations)
        })

    return pd.DataFrame(data).sort_values(by="Time", ascending=False)

def analyze(row):
    hour = row["Time"].hour

    if row["Motion"] == 1 and 1 <= hour <= 5:
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
st.markdown("""
<div class="cyber-title">
🏠 Smart Home Security Monitor with Intrusion Detection
</div>
""", unsafe_allow_html=True)

alarm_mode = st.toggle("🔔 Alarm System", value=True)
auto_refresh = st.toggle("🔄 Live Monitoring", value=True)

# ------------------ DATA ------------------
df = generate_data()
df["Status"] = df.apply(analyze, axis=1)
df["Risk"] = df["Status"].apply(get_risk)

alerts = df[df["Status"] != "✅ Normal"]

# ------------------ FLASH EFFECT ------------------
if st.session_state.intrusion and alarm_mode:
    st.markdown('<div class="flash">', unsafe_allow_html=True)

# ------------------ STATUS ------------------
st.markdown("### 🛡️ System Status")

if st.session_state.intrusion:
    st.markdown("<div class='siren'>🚨 INTRUSION DETECTED 🚨</div>", unsafe_allow_html=True)
else:
    st.markdown("<p class='alert-green'>✅ SYSTEM SECURE</p>", unsafe_allow_html=True)

# ------------------ DASHBOARD ------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📊 Sensor Data")
    show_df = df.copy()
    show_df["Time"] = show_df["Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    st.dataframe(show_df, use_container_width=True)
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
m1.metric("Events", len(df))
m2.metric("Alerts", len(alerts))
m3.metric("Failed Attempts", st.session_state.failed_attempts)

# ------------------ CHARTS ------------------
st.markdown("### 📈 Activity Insights")

chart_df = df.copy()
chart_df["Hour"] = chart_df["Time"].dt.hour

st.line_chart(chart_df.groupby("Hour")["Motion"].sum())
st.bar_chart(chart_df["Location"].value_counts())

# ------------------ ACCESS PANEL ------------------
st.markdown("### 🔐 Access Control Panel")

user_code = st.text_input("Enter Access Code", type="password")

if st.button("Authorize Access"):
    result = check_access(user_code)

    if "Intruder" in result or "LOCKED" in result:
        if alarm_mode:
            st.error(result)
            st.warning("🔊 SECURITY ALARM ACTIVATED")

            st.markdown("""
            <audio autoplay loop>
                <source src="https://www.soundjay.com/mechanical/sounds/alarm-01.wav">
            </audio>
            """, unsafe_allow_html=True)
        else:
            st.warning(result)
    else:
        st.success(result)

# ------------------ SECURITY LOG ------------------
if st.session_state.alerts_list:
    st.markdown("### 🚨 Security Log")
    for alert in st.session_state.alerts_list:
        st.write(alert)

# ------------------ CLOSE FLASH DIV ------------------
if st.session_state.intrusion and alarm_mode:
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------ AUTO REFRESH ------------------
if auto_refresh:
    time.sleep(5)
    st.rerun()

# ------------------ FOOTER ------------------
st.markdown("---")
st.markdown("🔒 Advanced Smart Security System | Hackathon Project")
