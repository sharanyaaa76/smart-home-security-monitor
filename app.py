import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Smart Home Security", layout="wide")

# ------------------ ACCESS CODE ------------------
CORRECT_CODE = "1234"
alerts_list = []

def check_access(input_code):
    if input_code == CORRECT_CODE:
        return "✅ Access Granted"
    else:
        alerts_list.append("🚨 Intruder detected via wrong code!")
        return "🚨 SUSPICIOUS ACTIVITY, INTRUDER DETECTED"

# ------------------ DATA GENERATION ------------------
def generate_data():
    data = []
    current_time = datetime.now()

    for i in range(30):
        data.append({
            "Time": current_time - timedelta(minutes=i*5),
            "Motion": random.choice([0, 1]),
            "Door": random.choice(["Open", "Closed"])
        })

    return pd.DataFrame(data)

# ------------------ ANALYSIS ------------------
def analyze(row):
    hour = row["Time"].hour

    if row["Motion"] == 1 and (1 <= hour <= 5):
        return "⚠️ Late Night Movement"

    if row["Motion"] == 1 and row["Door"] == "Closed":
        return "⚠️ Unexpected Movement"

    return "✅ Normal"

# ------------------ UI ------------------
st.title("🏠 Smart Home Security Monitor")

st.markdown("### Real-time Monitoring & Intrusion Detection System")

df = generate_data()
df["Status"] = df.apply(analyze, axis=1)

# ------------------ DASHBOARD ------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Sensor Data")
    st.dataframe(df)

with col2:
    st.subheader("🚨 Alerts")

    alerts = df[df["Status"] != "✅ Normal"]

    if len(alerts) == 0:
        st.success("No suspicious activity detected")
    else:
        st.error("Suspicious activities detected!")
        st.dataframe(alerts)

# ------------------ METRICS ------------------
st.markdown("### 📈 System Metrics")

m1, m2 = st.columns(2)

m1.metric("Total Events", len(df))
m2.metric("Alerts Detected", len(alerts))

# ------------------ ACCESS SYSTEM ------------------
st.markdown("### 🔐 Door Access System")

user_code = st.text_input("Enter Access Code", type="password")

if st.button("Unlock Door"):
    result = check_access(user_code)

    if "SUSPICIOUS" in result:
        st.error(result)
    else:
        st.success(result)

# ------------------ SECURITY LOG ------------------
if len(alerts_list) > 0:
    st.markdown("### 🚨 Security Log")
    for alert in alerts_list:
        st.write(alert)
