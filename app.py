import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Smart Home Security Monitor", layout="wide")

# ------------------ ACCESS CODE ------------------
CORRECT_CODE = "1234"
alerts_list = []

def check_access(input_code):
    if input_code == CORRECT_CODE:
        return "✅ Access Granted"
    else:
        alerts_list.append("🚨 Intruder detected via wrong access code!")
        return "🚨 SUSPICIOUS ACTIVITY, INTRUDER DETECTED"

# ------------------ RANDOM DATA GENERATION ------------------
def generate_data():
    data = []
    current_time = datetime.now()

    for _ in range(40):
        # Random time within last 24 hours
        random_minutes = random.randint(0, 1440)
        random_time = current_time - timedelta(minutes=random_minutes)

        data.append({
            "Time": random_time,
            "Motion": random.choice([0, 1]),
            "Door": random.choice(["Open", "Closed"])
        })

    df = pd.DataFrame(data)

    # Sort latest first
    df = df.sort_values(by="Time", ascending=False)

    # Format time for display
    df["Time"] = df["Time"].dt.strftime("%Y-%m-%d %H:%M:%S")

    return df

# ------------------ ANOMALY DETECTION ------------------
def analyze(row):
    hour = int(row["Time"].split()[1].split(":")[0])

    if row["Motion"] == 1 and (1 <= hour <= 5):
        return "⚠️ Late Night Movement"

    if row["Motion"] == 1 and row["Door"] == "Closed":
        return "⚠️ Motion Without Door Open"

    return "✅ Normal"

# ------------------ UI ------------------
st.title("🏠 Smart Home Security Monitor")
st.markdown("### Real-time Monitoring | Intrusion Detection | Smart Alerts")

# Generate Data
df = generate_data()
df["Status"] = df.apply(analyze, axis=1)

# ------------------ DASHBOARD ------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Sensor Data")
    st.dataframe(df, use_container_width=True)

with col2:
    st.subheader("🚨 Alerts")

    alerts = df[df["Status"] != "✅ Normal"]

    if alerts.empty:
        st.success("No suspicious activity detected")
    else:
        st.error("Suspicious activities detected!")
        st.dataframe(alerts, use_container_width=True)

# ------------------ METRICS ------------------
st.markdown("### 📈 System Metrics")

m1, m2 = st.columns(2)
m1.metric("Total Events", len(df))
m2.metric("Alerts Detected", len(alerts))

# ------------------ ACCESS CONTROL ------------------
st.markdown("### 🔐 Door Access System")

user_code = st.text_input("Enter Access Code", type="password")

if st.button("Unlock Door"):
    result = check_access(user_code)

    if "SUSPICIOUS" in result:
        st.error(result)
    else:
        st.success(result)

# ------------------ SECURITY LOG ------------------
if alerts_list:
    st.markdown("### 🚨 Security Log")
    for alert in alerts_list:
        st.write(alert)

# ------------------ FOOTER ------------------
st.markdown("---")
st.markdown("🔒 Smart Home Security System | Built using Python & Streamlit")
