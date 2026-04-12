import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
import time

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Smart Home Security Monitor", layout="wide")

# ------------------ FULL SCREEN FLASH CSS ------------------
st.markdown("""
<style>

/* Base */
body { background-color: #0b0f19; }
.main { background-color: #0b0f19; color: #e0e0e0; }

/* Title */
.cyber-title {
    font-size: 36px;
    text-align: center;
    color: #00ffcc;
    text-shadow: 0px 0px 10px #00ffcc;
}

/* Cards */
.card {
    background-color: #121826;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0,255,204,0.2);
}

/* FULL SCREEN FLASH */
.flash-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 9999;
    opacity: 0.6;
    animation-duration: 2s;
    animation-fill-mode: forwards;
}

/* RED */
.flash-red {
    background-color: red;
}

/* GREEN */
.flash-green {
    background-color: green;
}

</style>
""", unsafe_allow_html=True)

# ------------------ SESSION ------------------
if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0

if "alerts_list" not in st.session_state:
    st.session_state.alerts_list = []

if "flash_type" not in st.session_state:
    st.session_state.flash_type = None

# ------------------ ACCESS ------------------
CORRECT_CODE = "1234"

def check_access(code):
    if st.session_state.failed_attempts >= 3:
        return "⛔ SYSTEM LOCKED!"

    if code == CORRECT_CODE:
        st.session_state.failed_attempts = 0
        return "✅ Access Granted"
    else:
        st.session_state.failed_attempts += 1
        msg = f"🚨 Intruder! Attempts: {st.session_state.failed_attempts}/3"
        st.session_state.alerts_list.append(msg)
        return msg

# ------------------ HEADER ------------------
st.markdown("""
<div class="cyber-title">
🏠 Smart Home Security Monitor with Intrusion Detection
</div>
""", unsafe_allow_html=True)

# ------------------ FLASH LOGIC ------------------
if st.session_state.flash_type == "red":
    st.markdown('<div class="flash-overlay flash-red"></div>', unsafe_allow_html=True)
    time.sleep(2)
    st.session_state.flash_type = None
    st.rerun()

elif st.session_state.flash_type == "green":
    st.markdown('<div class="flash-overlay flash-green"></div>', unsafe_allow_html=True)
    time.sleep(2)
    st.session_state.flash_type = None
    st.rerun()

# ------------------ TOGGLES ------------------
alarm_mode = st.toggle("🔔 Alarm System ON/OFF", True)
auto_refresh = st.toggle("🔄 Live Monitoring", True)

# ------------------ DATA ------------------
def generate_data():
    now = datetime.now()
    locations = ["Entrance", "Living Room", "Bedroom", "Garage"]

    data = []
    for _ in range(40):
        t = now - timedelta(minutes=random.randint(0, 1440))
        data.append({
            "Time": t,
            "Motion": random.choice([0, 1]),
            "Door": random.choice(["Open", "Closed"]),
            "Location": random.choice(locations)
        })

    return pd.DataFrame(data).sort_values(by="Time", ascending=False)

df = generate_data()

def analyze(row):
    hour = row["Time"].hour
    if row["Motion"] == 1 and 1 <= hour <= 5:
        return "⚠️ Late Night Movement"
    if row["Motion"] == 1 and row["Door"] == "Closed":
        return "⚠️ Motion Without Door Open"
    return "✅ Normal"

df["Status"] = df.apply(analyze, axis=1)
alerts = df[df["Status"] != "✅ Normal"]

# ------------------ STATUS ------------------
st.markdown("### 🛡️ System Status")

if len(alerts) > 0:
    st.error("🚨 SYSTEM UNDER THREAT")
else:
    st.success("✅ SYSTEM SECURE")

# ------------------ DASHBOARD ------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📊 Sensor Data")

    df_show = df.copy()
    df_show["Time"] = df_show["Time"].dt.strftime("%Y-%m-%d %H:%M:%S")

    st.dataframe(df_show)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🚨 Alerts")

    if alerts.empty:
        st.success("No threats detected")
    else:
        st.error("Threats detected")
        st.dataframe(alerts)

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ METRICS ------------------
m1, m2 = st.columns(2)
m1.metric("Events", len(df))
m2.metric("Alerts", len(alerts))

# ------------------ ACCESS PANEL ------------------
st.markdown("### 🔐 Access Control")

code = st.text_input("Enter Access Code", type="password")

if st.button("Authorize Access"):
    result = check_access(code)

    if "Intruder" in result or "LOCKED" in result:
        st.session_state.flash_type = "red"
        st.error(result)
    else:
        st.session_state.flash_type = "green"
        st.success(result)

# ------------------ LOG ------------------
if st.session_state.alerts_list:
    st.markdown("### 🚨 Security Log")
    for a in st.session_state.alerts_list:
        st.write(a)

# ------------------ AUTO REFRESH ------------------
if auto_refresh:
    time.sleep(5)
    st.rerun()
