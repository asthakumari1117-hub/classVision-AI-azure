import streamlit as st
import requests
import io
from PIL import Image
import tempfile
import time
import csv
from datetime import datetime

# -------------------------------
# 🔑 AZURE CONFIG
# -------------------------------
PREDICTION_URL = "https://aictevision-prediction.cognitiveservices.azure.com/customvision/v3.0/Prediction/b50c13dc-3ea3-4cf3-ad2d-d4511ab52293/classify/iterations/classroom-attention-model/image"
PREDICTION_KEY = "B7sEyTgbUWzj6VHSFTg1twgHBn3DLHlo5kntOLH5w3XOz5DWJgr2JQQJ99CBACYeBjFXJ3w3AAAIACOGIeDe"



HEADERS = {
    "Prediction-Key": PREDICTION_KEY,
    "Content-Type": "application/octet-stream"
}

# -------------------------------
# 🎨 UI SETUP
# -------------------------------
st.set_page_config("Class Attention App", layout="centered")
st.title("📊 Class Attention")
st.subheader("Attention Level")

uploaded_file = st.file_uploader(
    "📤 Upload classroom image",
    type=["jpg", "jpeg", "png"]
)

# Initialize session state
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# -------------------------------
# 📸 TEST ATTENTION
# -------------------------------
if uploaded_file is not None:
    st.success("✅ Image uploaded")

    if st.button("📷 Test Attention"):
        image = Image.open(uploaded_file).convert("RGB")
        image.thumbnail((1024, 1024))  # Azure safe size

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        image_bytes = buffer.getvalue()

        response = requests.post(
            PREDICTION_URL,
            headers=HEADERS,
            data=image_bytes
        )

        if response.status_code != 200:
            st.error("❌ Azure error")
            st.text(response.text)
        else:
            result = response.json()
            best = max(result["predictions"], key=lambda x: x["probability"])

            tag = best["tagName"]
            prob = round(best["probability"] * 100, 2)
            # ✅ SAVE RESULT FOR MARK ATTENDANCE (CRITICAL)
            st.session_state.last_result = (tag, prob)

            if tag == "Focused":
                st.success(f"🟢 Focused ({prob}%)")
            elif tag == "Looking_Away":
                st.warning(f"🟡 Looking Away ({prob}%)")
            else:
                st.error(f"🔴 Sleeping ({prob}%)")
else:
    st.warning("⚠️ Please upload an image first")

# -------------------------------
# 📝 MARK ATTENDANCE
# -------------------------------
if st.button("📝 Mark Attendance"):

    if st.session_state.last_result is None:
        st.warning("⚠️ Please test attention first")
    else:
        tag, prob = st.session_state.last_result
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open("attendance.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([time_now, tag, prob])

        st.success("✅ Attendance marked successfully")

# -------------------------------
# 👤 STUDENT PROFILE (WORKING)
# -------------------------------
st.divider()
st.subheader("👤 Student Profile")

with st.form("student_profile_form"):

    name = st.text_input("Student Name")
    roll = st.text_input("Roll Number")
    branch = st.text_input("Branch")
    year = st.selectbox("Year", ["1st", "2nd", "3rd", "4th"])

    submit_profile = st.form_submit_button("💾 Save Profile")

    if submit_profile:
        if name == "" or roll == "" or branch == "":
            st.warning("⚠️ Please fill all fields")
        else:
            with open("students.csv", "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([roll, name, branch, year])

            st.success("✅ Student profile saved successfully")


# -------------------------------
# ❌ EXIT
# -------------------------------
if st.button("❌ Exit"):
    st.warning("App stopped. Close browser tab.")
