import streamlit as st
import requests, io, csv, os, hashlib
from PIL import Image
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
# 🔐 UTILS
# -------------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(file, username, password, role):
    if not os.path.exists(file):
        return None
    with open(file, "r") as f:
        reader = csv.reader(f)
        for r in reader:
            if r[0] == username and r[4] == hash_password(password):
                return {
                    "username": r[0],
                    "name": r[1],
                    "email": r[2],
                    "phone": r[3],
                    "photo": r[5],
                    "role": role
                }
    return None

def update_user_profile(csv_file, username, name, email, phone, photo_path):
    rows, updated = [], None
    with open(csv_file, "r") as f:
        reader = csv.reader(f)
        for r in reader:
            if r[0] == username:
                r[1], r[2], r[3], r[5] = name, email, phone, photo_path
                updated = r
            rows.append(r)
    with open(csv_file, "w", newline="") as f:
        csv.writer(f).writerows(rows)
    return updated

# -------------------------------
# 🧠 SESSION STATE
# -------------------------------
for k in ["logged_in", "user", "role", "session_info"]:
    if k not in st.session_state:
        st.session_state[k] = None

st.set_page_config("ClassVision AI", layout="wide")

# ===============================
# 🔐 AUTHENTICATION
# ===============================
if not st.session_state.logged_in:
    st.title("🔐 ClassVision AI Login")

    role_ui = st.radio("Login as", ["👩‍🏫 Teacher", "🎓 Student"])
    tab_login, tab_signup = st.tabs(["🔐 Login", "🆕 Create Account"])

    # ---------- LOGIN ----------
    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Username / Roll No")
            password = st.text_input("Password", type="password")
            login = st.form_submit_button("Login")

            if login:
                file = "teachers.csv" if role_ui == "👩‍🏫 Teacher" else "students.csv"
                role = "teacher" if role_ui == "👩‍🏫 Teacher" else "student"

                user = authenticate_user(file, username, password, role)

                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.session_state.role = role
                    st.success("✅ Login successful")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")

    # ---------- SIGN UP ----------
    with tab_signup:
        with st.form("signup_form"):
            username = st.text_input("Username / Roll No")
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            password = st.text_input("Password", type="password")
            photo = st.file_uploader("Upload Photo", ["jpg", "png"])
            signup = st.form_submit_button("Create Account")

            if signup:
                if not all([username, name, email, phone, password, photo]):
                    st.warning("⚠️ All fields are required")
                else:
                    folder = "teacher_photos" if role_ui == "👩‍🏫 Teacher" else "student_photos"
                    file = "teachers.csv" if role_ui == "👩‍🏫 Teacher" else "students.csv"
                    os.makedirs(folder, exist_ok=True)

                    photo_path = f"{folder}/{username}.jpg"
                    with open(photo_path, "wb") as f:
                        f.write(photo.getbuffer())

                    with open(file, "a", newline="") as f:
                        csv.writer(f).writerow([
                            username,
                            name,
                            email,
                            phone,
                            hash_password(password),
                            photo_path
                        ])

                    st.success("✅ Account created. Please login.")

    st.stop()
# ===============================
# 📊 SIDEBAR
# ===============================
st.sidebar.title("📊 ClassVision AI")
st.sidebar.write(f"👤 {st.session_state.user['name']}")

if st.sidebar.button("🚪 Logout"):
    st.session_state.clear()
    st.rerun()

# ===============================
# 👩‍🏫 TEACHER VIEW
# ===============================
if st.session_state.role == "teacher":

    menu = st.sidebar.radio("Navigation", ["🏠 Home", "📸 Test Attention", "📝 Attendance", "👤 My Profile"])

    # 🏠 HOME
    if menu == "🏠 Home":
        st.title("👩‍🏫 Teacher Dashboard")
        total, focused = 0, 0
        if os.path.exists("attendance.csv"):
            with open("attendance.csv") as f:
                for r in csv.reader(f):
                    if len(r) < 6: continue
                    total += 1
                    if r[4] == "Focused":
                        focused += 1
        col1, col2, col3 = st.columns(3)
        col1.metric("📊 Records", total)
        col2.metric("🟢 Focused", focused)
        col3.metric("🎯 Focus %", round((focused/total)*100, 2) if total else 0)

    # 📸 TEST ATTENTION
    elif menu == "📸 Test Attention":
        st.header("📸 Test Attention")

        with st.form("session"):
            cls = st.text_input("Class")
            sub = st.text_input("Subject")
            if st.form_submit_button("▶ Start Session"):
                st.session_state.session_info = {
                    "class": cls,
                    "subject": sub,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "start_ts": datetime.now()
                }

        if not st.session_state.session_info:
            st.warning("Start session first")
            st.stop()

        source = st.radio("Image Source", ["📷 Camera", "🖼️ Upload"])
        img = st.camera_input("Capture") if source == "📷 Camera" else st.file_uploader("Upload", ["jpg","png"])

        if img and st.button("Analyze"):
            image = Image.open(img).convert("RGB")
            buf = io.BytesIO()
            image.save(buf, format="JPEG")
            res = requests.post(PREDICTION_URL, headers=HEADERS, data=buf.getvalue())
            if res.status_code == 200:
                best = max(res.json()["predictions"], key=lambda x: x["probability"])
                prob = round(best["probability"], 4)
                tag = best["tagName"]
                st.success(f"{tag} ({prob*100:.2f}%)")
                with open("attendance.csv", "a", newline="") as f:
                    csv.writer(f).writerow([
                        st.session_state.session_info["date"],
                        st.session_state.session_info["class"],
                        st.session_state.session_info["subject"],
                        st.session_state.user["username"],
                        tag,
                        prob
                    ])

        if "start_ts" in st.session_state.session_info:
            if (datetime.now() - st.session_state.session_info["start_ts"]).seconds >= 300:
                st.info("⏱ 5 minutes passed — capture again")

    # 📝 ATTENDANCE
    elif menu == "📝 Attendance":
        st.header("📝 Attendance Records")
        fc = st.text_input("Class")
        fs = st.text_input("Subject")
        fd = st.date_input("Date")
        rows = []
        if os.path.exists("attendance.csv"):
            with open("attendance.csv") as f:
                for r in csv.reader(f):
                    if len(r) < 6: continue
                    if ((not fc or r[1]==fc) and (not fs or r[2]==fs) and (not fd or r[0]==fd.strftime("%Y-%m-%d"))):
                        rows.append(r)
        if rows:
            st.dataframe(rows, use_container_width=True)
        else:
            st.info("No records")

    # 👤 MY PROFILE
    elif menu == "👤 My Profile":
        u = st.session_state.user
        st.header("👤 My Profile")
        st.image(u["photo"], width=180)

        with st.form("edit"):
            name = st.text_input("Name", u["name"])
            email = st.text_input("Email", u["email"])
            phone = st.text_input("Phone", u["phone"])
            photo = st.file_uploader("Change Photo", ["jpg","png"])
            if st.form_submit_button("Save"):
                path = u["photo"]
                if photo:
                    os.makedirs("teacher_photos", exist_ok=True)
                    path = f"teacher_photos/{u['username']}.jpg"
                    open(path,"wb").write(photo.getbuffer())
                up = update_user_profile("teachers.csv", u["username"], name, email, phone, path)
                if up:
                    st.session_state.user.update({"name":up[1],"email":up[2],"phone":up[3],"photo":up[5]})
                    st.success("Profile updated")
                    st.rerun()

# ===============================
# 🎓 STUDENT VIEW
# ===============================
if st.session_state.role == "student":

    menu = st.sidebar.radio(
        "Navigation",
        ["🏠 Home", "📸 Study Monitoring", "📊 My Attendance", "👤 My Profile"]
    )

    # ---------- HOME ----------
    if menu == "🏠 Home":
        st.title("🎓 Student Dashboard")
        st.info("Welcome! Use the sidebar to monitor your study behaviour and attendance.")

    # ---------- STUDY MONITORING ----------
    elif menu == "📸 Study Monitoring":
        st.header("📸 Study Monitoring")
        st.info("Choose camera or upload an image to analyze your study behaviour")

        source = st.radio(
            "Select Image Source",
            ["📷 Camera", "🖼️ Upload Image"]
        )

        image_input = None

        if source == "📷 Camera":
            image_input = st.camera_input("Capture Image")

        elif source == "🖼️ Upload Image":
            image_input = st.file_uploader(
                "Upload Image",
                type=["jpg", "jpeg", "png"]
            )

        if image_input and st.button("🔍 Analyze Behaviour"):
            image = Image.open(image_input).convert("RGB")
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=85)

            response = requests.post(
                PREDICTION_URL,
                headers=HEADERS,
                data=buffer.getvalue()
            )

            if response.status_code != 200:
                st.error("❌ Azure prediction failed")
            else:
                result = response.json()
                best = max(result["predictions"], key=lambda x: x["probability"])

                tag = best["tagName"]
                prob = round(best["probability"] * 100, 2)

                if tag == "Focused":
                    st.success(f"🟢 Focused ({prob}%)")
                elif tag == "Looking_Away":
                    st.warning(f"🟡 Looking Away ({prob}%)")
                else:
                    st.error(f"🔴 Sleeping ({prob}%)")

                # ✅ SAVE ATTENDANCE
                with open("attendance.csv", "a", newline="") as f:
                    csv.writer(f).writerow([
                        datetime.now().strftime("%Y-%m-%d"),
                        "Self Study",
                        "Student Monitoring",
                        st.session_state.user["username"],
                        tag,
                        prob / 100
                    ])

                st.success("✅ Attendance saved automatically")

    # ---------- MY ATTENDANCE ----------
    elif menu == "📊 My Attendance":
        st.header("📊 My Attendance")

        rows = []

        if os.path.exists("attendance.csv"):
            with open("attendance.csv", "r") as f:
                reader = csv.reader(f)
                for r in reader:
                    if len(r) >= 6 and r[3] == st.session_state.user["username"]:
                        rows.append(r)

        if not rows:
            st.info("ℹ️ No attendance records found yet.")
        else:
            st.table(
                [["Date", "Class", "Subject", "Status", "Confidence"]] +
                [[r[0], r[1], r[2], r[4], f"{float(r[5]) * 100:.2f}%"] for r in rows]
            )

            focused = sum(1 for r in rows if r[4] == "Focused")
            away = sum(1 for r in rows if r[4] == "Looking_Away")
            sleep = sum(1 for r in rows if r[4] == "Sleeping")
            total = len(rows)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📊 Total Classes", total)
            col2.metric("🟢 Focused", focused)
            col3.metric("🟡 Looking Away", away)
            col4.metric("🔴 Sleeping", sleep)

            score = round((focused / total) * 100, 2) if total else 0
            st.progress(score / 100)
            st.write(f"🎯 **Study Score:** {score}%")

    # ---------- MY PROFILE ----------
    elif menu == "👤 My Profile":
        st.header("👤 My Profile")

        u = st.session_state.user
        st.image(u["photo"], width=180)

        st.subheader("✏️ Edit Profile")

        with st.form("edit_profile_form"):
            new_name = st.text_input("Name", value=u["name"])
            new_email = st.text_input("Email", value=u["email"])
            new_phone = st.text_input("Phone", value=u["phone"])
            new_photo = st.file_uploader(
                "Change Profile Photo (optional)",
                ["jpg", "png"]
            )

            save = st.form_submit_button("💾 Save Changes")

        if save:
            photo_path = u["photo"]

            if new_photo:
                os.makedirs("student_photos", exist_ok=True)
                photo_path = f"student_photos/{u['username']}.jpg"
                with open(photo_path, "wb") as f:
                    f.write(new_photo.getbuffer())

            updated = update_user_profile(
                "students.csv",
                u["username"],
                new_name,
                new_email,
                new_phone,
                photo_path
            )

            if updated:
                st.session_state.user.update({
                    "name": updated[1],
                    "email": updated[2],
                    "phone": updated[3],
                    "photo": updated[5]
                })
                st.success("✅ Profile updated successfully")
                st.rerun()