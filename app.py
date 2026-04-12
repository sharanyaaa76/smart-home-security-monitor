import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
import time
from PIL import Image, ImageDraw, ImageFont

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Smart Home Security Monitor", layout="wide")

# ------------------ CSS ------------------
st.markdown("""
<style>
body { background-color: #0b0f19; }
.main { background-color: #0b0f19; color: #e0e0e0; }

.cyber-title {
    font-size: 36px;
    text-align: center;
    color: #00ffcc;
    text-shadow: 0px 0px 10px #00ffcc;
}

.overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 99999;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 60px;
    font-weight: bold;
    color: white;
    text-shadow: 0px 0px 20px black;
}

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

.flash-red { animation: blinkRed 0.5s infinite; }
.flash-green { animation: blinkGreen 0.5s infinite; }

</style>
""", unsafe_allow_html=True)

# ------------------ SESSION ------------------
if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0

if "alerts_list" not in st.session_state:
    st.session_state.alerts_list = []

if "flash_type" not in st.session_state:
    st.session_state.flash_type = None

if "intruder_image" not in st.session_state:
    st.session_state.intruder_image = None

# ------------------ ACCESS ------------------
CORRECT_CODE = "1234"

def check_access(code):
    if st.session_state.failed_attempts >= 3:
        return "LOCKED"

    if code == CORRECT_CODE:
        st.session_state.failed_attempts = 0
        return "GRANTED"
    else:
        st.session_state.failed_attempts += 1
        st.session_state.alerts_list.append("🚨 Intruder attempt")
        return "DENIED"

# ------------------ HEADER ------------------
st.markdown("""
<div class="cyber-title">
🏠 Smart Home Security Monitor with Intrusion Detection
</div>
""", unsafe_allow_html=True)

# ------------------ FLASH ------------------
if st.session_state.flash_type == "red":
    st.markdown("""
    <div class="overlay flash-red">
        🚨 ACCESS DENIED 🚨
    </div>
    """, unsafe_allow_html=True)
    time.sleep(2)
    st.session_state.flash_type = None
    st.rerun()

elif st.session_state.flash_type == "green":
    st.markdown("""
    <div class="overlay flash-green">
        ✅ ACCESS GRANTED ✅
    </div>
    """, unsafe_allow_html=True)
    time.sleep(2)
    st.session_state.flash_type = None
    st.rerun()

# ------------------ CAMERA ------------------
st.markdown("### 📷 Security Camera Feed")
camera_image = st.camera_input("Activate Camera")

# ------------------ FAKE AUTO CAPTURE ------------------
def create_intruder_snapshot(image):
    img = Image.open(image)

    draw = ImageDraw.Draw(img)
    text = f"INTRUDER DETECTED\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nLocation: Entrance"

    draw.text((10, 10), text, fill="red")

    return img

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

# ------------------ DASHBOARD ------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Sensor Data")
    df_show = df.copy()
    df_show["Time"] = df_show["Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    st.dataframe(df_show)

with col2:
    st.subheader("🚨 Alerts")
    if alerts.empty:
        st.success("No threats detected")
    else:
        st.error("Threats detected")
        st.dataframe(alerts)

# ------------------ ACCESS ------------------
st.markdown("### 🔐 Access Control")

code = st.text_input("Enter Access Code", type="password")

if st.button("Authorize Access"):
    result = check_access(code)

    if result == "DENIED" or result == "LOCKED":
        st.session_state.flash_type = "red"

        # 📸 SMART AUTO CAPTURE
        if camera_image is not None:
            img = create_intruder_snapshot(camera_image)
            st.session_state.intruder_image = img
        else:
            st.warning("Camera not active — using simulated capture")

    else:
        st.session_state.flash_type = "green"

# ------------------ SHOW IMAGE ------------------
if st.session_state.intruder_image is not None:
    st.markdown("### 🚨 Intruder Snapshot")
    st.image(st.session_state.intruder_image)

# ------------------ LOG ------------------
if st.session_state.alerts_list:
    st.markdown("### 🚨 Security Log")
    for a in st.session_state.alerts_list:
        st.write(a)

# ------------------ AUTO REFRESH ------------------
time.sleep(5)
st.rerun()
