import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
import time

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Smart Home Security Monitor", layout="wide")

# ------------------ CSS (FULL SCREEN BLINK EFFECT) ------------------
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

/* FULL SCREEN OVERLAY */
.overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 9999;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 50px;
    font-weight: bold;
    color: white;
}

/* BLINK ANIMATION */
@keyframes blinkRed {
    0% { background-color: red; }
    50% { background-color: #330000; }
    100% { background-color: red; }
}

@keyframes blinkGreen {
    0% { background-color: green; }
    50% { background-color: #003300; }
    100% { background-color: green; }
}

.flash-red {
    animation: blinkRed 0.5s infinite;
}

.flash-green {
    animation: blinkGreen 0.5s infinite;
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
        return "GRANTED"
    else:
        st.session_state.failed_attempts += 1
        msg = f"🚨 Intruder! Attempts: {st.session_state.failed_attempts}/3"
        st.session_state.alerts_list.append(msg)
        return "DENIED"

# ------------------ HEADER ------------------
st.markdown("""
<div class="cyber-title">
🏠 Smart Home Security Monitor with Intrusion Detection
</div>
""", unsafe_allow_html=True)

# ------------------ FLASH EFFECT ------------------
if st.session_state.flash_type == "red":
    st.markdown("""
    <div class="overlay flash-red">
        ACCESS DENIED
    </div>
    """, unsafe_allow_html=True)
    time.sleep(2)
    st.session_state.flash_type = None
    st.rerun()

elif st.session_state.flash_type == "green":
    st.markdown("""
    <div class="overlay flash-green">
        ACCESS GRANTED
    </div>
    """, unsafe_allow_html=True)
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

# ------------------ ACCESS PANEL ------------------
st.markdown("### 🔐 Access Control")

code = st.text_input("Enter Access Code", type="password")

if st.button("Authorize Access"):
    result = check_access(code)

    if result == "DENIED" or "LOCKED" in result:
        st.session_state.flash_type = "red"
    else:
        st.session_state.flash_type = "green"

# ------------------ LOG ------------------
if st.session_state.alerts_list:
    st.markdown("### 🚨 Security Log")
    for a in st.session_state.alerts_list:
        st.write(a)

# ------------------ AUTO REFRESH ------------------
if auto_refresh:
    time.sleep(5)
    st.rerun()
