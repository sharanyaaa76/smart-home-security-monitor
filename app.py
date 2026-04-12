import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
import time

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Smart Home Security Monitor", layout="wide")

# ------------------ CYBER UI + ANIMATIONS ------------------
st.markdown("""
<style>

/* Base */
body { background-color: #0b0f19; }
.main { background-color: #0b0f19; color: #e0e0e0; }

/* Title */
.cyber-title {
    font-size: 38px;
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
}

/* Flash screen */
@keyframes flashRed {
    0% { background-color: #0b0f19; }
    50% { background-color: rgba(255,0,0,0.6); }
    100% { background-color: #0b0f19; }
}
.flash { animation: flashRed 1s infinite; }

/* Siren */
@keyframes blink {
    0% { color: red; }
    50% { color: white; }
    100% { color: red; }
}
.siren {
    font-size: 28px;
    text-align: center;
    animation: blink 1s infinite;
}

</style>
""", unsafe_allow_html=True)

# ------------------ SESSION ------------------
if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0

if "alerts_list" not in st.session_state:
    st.session_state.alerts_list = []

if "intrusion" not in st.session_state:
    st.session_state.intrusion = False

# ------------------ ACCESS CONTROL ------------------
CORRECT_CODE = "1234"

def check_access(code):
    if st.session_state.failed_attempts >= 3:
        st.session_state.intrusion = True
        return "⛔ SYSTEM LOCKED!"

    if code == CORRECT_CODE:
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

def analyze(row):
    hour = row["Time"].hour
    if row["Motion"] == 1 and 1 <= hour <= 5:
        return "⚠️ Late Night Movement"
    if row["Motion"] == 1 and row["Door"] == "Closed":
        return "⚠️ Motion Without Door Open"
    return "✅ Normal"

# ------------------ HEADER ------------------
st.markdown("""
<div class="cyber-title">
🏠 Smart Home Security Monitor with Intrusion Detection
</div>
""", unsafe_allow_html=True)

alarm_mode = st.toggle("🔔 Alarm System", True)
auto_refresh = st.toggle("🔄 Live Monitoring", True)

# ------------------ DATA PROCESS ------------------
df = generate_data()
df["Status"] = df.apply(analyze, axis=1)

alerts = df[df["Status"] != "✅ Normal"]

# ------------------ FLASH EFFECT ------------------
if st.session_state.intrusion and alarm_mode:
    st.markdown('<div class="flash">', unsafe_allow_html=True)

# ------------------ STATUS ------------------
st.markdown("### 🛡️ System Status")

if st.session_state.intrusion:
    st.markdown("<div class='siren'>🚨 INTRUSION DETECTED 🚨</div>", unsafe_allow_html=True)
else:
    st.success("SYSTEM SECURE")

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
        st.error(result)

        if alarm_mode:
            st.warning("🔊 ALARM ACTIVATED")

            # 🔊 FIXED ALARM SOUND
            st.markdown("""
            <script>
            var audio = new Audio("https://www.soundjay.com/mechanical/sounds/alarm-01.wav");
            audio.loop = true;
            audio.play();
            </script>
            """, unsafe_allow_html=True)

    else:
        st.success(result)

# ------------------ MANUAL ALARM BUTTON ------------------
if st.button("🔊 Play Alarm Manually"):
    st.markdown("""
    <script>
    var audio = new Audio("https://www.soundjay.com/mechanical/sounds/alarm-01.wav");
    audio.loop = true;
    audio.play();
    </script>
    """, unsafe_allow_html=True)

# ------------------ LOG ------------------
if st.session_state.alerts_list:
    st.markdown("### 🚨 Security Log")
    for a in st.session_state.alerts_list:
        st.write(a)

# ------------------ CLOSE FLASH ------------------
if st.session_state.intrusion and alarm_mode:
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ AUTO REFRESH ------------------
if auto_refresh:
    time.sleep(5)
    st.rerun()
