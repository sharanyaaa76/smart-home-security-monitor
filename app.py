import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
import time

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Smart Home Security Monitor", layout="wide")

# ------------------ OPTIONAL WHATSAPP (TWILIO) ------------------
# Add these in Streamlit Secrets if you want real WhatsApp:
# [twilio]
# account_sid="YOUR_SID"
# auth_token="YOUR_TOKEN"
# from_whatsapp="whatsapp:+14155238886"
# to_whatsapp="whatsapp:+91XXXXXXXXXX"

def send_whatsapp_alert(message):
    try:
        from twilio.rest import Client
        creds = st.secrets["twilio"]
        client = Client(creds["account_sid"], creds["auth_token"])
        client.messages.create(
            body=message,
            from_=creds["from_whatsapp"],
            to=creds["to_whatsapp"]
        )
        return True
    except Exception:
        return False  # fallback if not configured

# ------------------ ACCESS CODE ------------------
CORRECT_CODE = "1234"
if "alerts_list" not in st.session_state:
    st.session_state.alerts_list = []

def check_access(input_code):
    if input_code == CORRECT_CODE:
        return "✅ Access Granted"
    else:
        msg = "🚨 Intruder detected via wrong access code!"
        st.session_state.alerts_list.append(msg)

        # Try WhatsApp (optional)
        sent = send_whatsapp_alert("🚨 ALERT: Wrong access code entered!")
        if sent:
            st.toast("WhatsApp alert sent 📱")

        return "🚨 SUSPICIOUS ACTIVITY, INTRUDER DETECTED"

# ------------------ DATA GENERATION ------------------
def generate_data(n=40):
    data = []
    now = datetime.now()

    for _ in range(n):
        mins = random.randint(0, 1440)
        t = now - timedelta(minutes=mins)
        data.append({
            "Time": t,
            "Motion": random.choice([0, 1]),
            "Door": random.choice(["Open", "Closed"])
        })

    df = pd.DataFrame(data).sort_values(by="Time", ascending=False)
    return df

# ------------------ ANALYSIS ------------------
def analyze(row):
    hour = row["Time"].hour

    if row["Motion"] == 1 and (1 <= hour <= 5):
        return "⚠️ Late Night Movement"

    if row["Motion"] == 1 and row["Door"] == "Closed":
        return "⚠️ Motion Without Door Open"

    return "✅ Normal"

# ------------------ HEADER ------------------
st.title("🏠 Smart Home Security Monitor")
st.caption("Real-time Monitoring • Intrusion Detection • Smart Alerts")

# ------------------ AUTO REFRESH ------------------
auto = st.toggle("🔄 Auto Refresh (every 5s)", value=True)

# ------------------ GENERATE + ANALYZE ------------------
df = generate_data()
df["Status"] = df.apply(analyze, axis=1)

alerts = df[df["Status"] != "✅ Normal"]

# ------------------ DASHBOARD ------------------
c1, c2 = st.columns(2)

with c1:
    st.subheader("📊 Sensor Data")
    show_df = df.copy()
    show_df["Time"] = show_df["Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    st.dataframe(show_df, use_container_width=True)

with c2:
    st.subheader("🚨 Alerts")
    if alerts.empty:
        st.success("No suspicious activity detected")
    else:
        st.error("Suspicious activities detected!")
        show_alerts = alerts.copy()
        show_alerts["Time"] = show_alerts["Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
        st.dataframe(show_alerts, use_container_width=True)

# ------------------ METRICS ------------------
m1, m2 = st.columns(2)
m1.metric("Total Events", len(df))
m2.metric("Alerts Detected", len(alerts))

# ------------------ CHARTS ------------------
st.markdown("### 📈 Activity Visualization")

chart_df = df.copy()
chart_df["Hour"] = chart_df["Time"].dt.hour

# Motion over time (count per hour)
motion_by_hour = chart_df.groupby("Hour")["Motion"].sum().reset_index()
st.line_chart(motion_by_hour.set_index("Hour"))

# Door status distribution
door_counts = chart_df["Door"].value_counts()
st.bar_chart(door_counts)

# ------------------ ACCESS CONTROL ------------------
st.markdown("### 🔐 Door Access System")

user_code = st.text_input("Enter Access Code", type="password")

if st.button("Unlock Door"):
    result = check_access(user_code)
    if "SUSPICIOUS" in result:
        st.error(result)
        st.warning("🔊 Alarm Triggered!")
    else:
        st.success(result)

# ------------------ SECURITY LOG ------------------
if st.session_state.alerts_list:
    st.markdown("### 🚨 Security Log")
    for a in st.session_state.alerts_list:
        st.write(a)

# ------------------ AUTO REFRESH LOOP ------------------
if auto:
    time.sleep(5)
    st.rerun()

# ------------------ FOOTER ------------------
st.markdown("---")
st.markdown("🔒 Built with Python & Streamlit • Hackathon Demo")
