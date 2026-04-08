import streamlit as st
import numpy as np
import cv2
import io, csv, os, hashlib
from PIL import Image
from datetime import datetime

# -------------------------------
# 🔁 LOCAL AI
# -------------------------------
def local_predict(image):
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    brightness = np.mean(gray)

    if brightness < 50:
        return "Sleeping", 0.85
    elif brightness < 120:
        return "Looking_Away", 0.75
    else:
        return "Focused", 0.90

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
# SESSION STATE
# -------------------------------
for k in ["logged_in", "user", "role"]:
    if k not in st.session_state:
        st.session_state[k] = None

st.set_page_config("ClassVision AI", layout="wide")

# ===============================
# LOGIN
# ===============================
if not st.session_state.logged_in:
    st.title("🔐 ClassVision AI Login")

    role_ui = st.radio("Login as", ["👩‍🏫 Teacher", "🎓 Student"])
    tab_login, tab_signup = st.tabs(["🔐 Login", "🆕 Create Account"])

    with tab_login:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            file = "teachers.csv" if role_ui=="👩‍🏫 Teacher" else "students.csv"
            role = "teacher" if role_ui=="👩‍🏫 Teacher" else "student"

            user = authenticate_user(file, username, password, role)

            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.session_state.role = role
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab_signup:
        username = st.text_input("New Username")
        name = st.text_input("Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        password = st.text_input("Password", type="password", key="signup_pass")
        photo = st.file_uploader("Upload Photo")

        if st.button("Create Account"):
            folder = "teacher_photos" if role_ui=="👩‍🏫 Teacher" else "student_photos"
            file = "teachers.csv" if role_ui=="👩‍🏫 Teacher" else "students.csv"

            os.makedirs(folder, exist_ok=True)
            path = f"{folder}/{username}.jpg"

            with open(path, "wb") as f:
                f.write(photo.getbuffer())

            with open(file, "a", newline="") as f:
                csv.writer(f).writerow([
                    username, name, email, phone,
                    hash_password(password), path
                ])

            st.success("Account created")

    st.stop()

# ===============================
# SIDEBAR
# ===============================
st.sidebar.title("📊 ClassVision AI")
st.sidebar.write(f"👤 {st.session_state.user['name']}")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()
# ===============================
# 👩‍🏫 TEACHER (FINAL CLEAN + FIXED)
# ===============================
if st.session_state.role == "teacher":

    menu = st.sidebar.radio(
        "Navigation",
        ["🏠 Home", "📸 Test Attention", "📝 Attendance", "👤 My Profile"]
    )

    # ===============================
    # 🏠 DASHBOARD
    # ===============================
    if menu == "🏠 Home":

        st.title("👩‍🏫 Teacher Dashboard")

        # -------- COURSE INFO --------
        st.subheader("📚 Course Details")

        course = st.text_input("Course (e.g. BCA, CSE)", key="course_input")
        subject = st.text_input("Subject (e.g. ML, DBMS)", key="subject_input")

        # -------- FILE UPLOAD --------
        st.subheader("📂 Upload Study Material")

        uploaded_file = st.file_uploader(
            "Upload Notes / PDF / Video",
            type=["pdf", "mp4", "jpg", "png"],
            key="teacher_upload"
        )

        if uploaded_file:
            os.makedirs("teacher_uploads", exist_ok=True)

            path = f"teacher_uploads/{uploaded_file.name}"

            with open(path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with open("materials.csv", "a", newline="") as f:
                csv.writer(f).writerow([
                    date,
                    course,
                    subject,
                    uploaded_file.name,
                    path
                ])

            st.success("✅ File Uploaded Successfully")

        # -------- STATS --------
        st.subheader("📊 Dashboard Stats")

        total, focused = 0, 0

        if os.path.exists("attendance.csv"):
            with open("attendance.csv") as f:
                for r in csv.reader(f):
                    if len(r) < 7:
                        continue
                    total += 1
                    if r[5] == "Focused":
                        focused += 1

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Records", total)
        col2.metric("Focused", focused)
        col3.metric("Focus %", round((focused / total) * 100, 2) if total else 0)

        # -------- MATERIALS --------
        st.subheader("📂 Uploaded Materials")

        if os.path.exists("materials.csv"):

            rows = list(csv.reader(open("materials.csv")))

            if rows:
                for i, r in enumerate(rows[::-1]):   # 🔥 FIXED (index added)

                    if len(r) < 5:
                        continue

                    date, course_val, subject_val, filename, path = r

                    c1, c2, c3, c4 = st.columns([2, 2, 2, 1])

                    c1.write(f"📅 {date}")
                    c2.write(f"📘 {course_val}")
                    c3.write(f"📖 {subject_val}")

                    # 🔥 FIXED UNIQUE KEY
                    if c4.button("Open", key=f"{path}_{i}"):

                        ext = path.split(".")[-1].lower()

                        if ext == "pdf":
                            with open(path, "rb") as f:
                                st.download_button(
                                    "Download PDF",
                                    f,
                                    file_name=filename,
                                    key=f"pdf_{i}"
                                )

                        elif ext == "mp4":
                            st.video(path)

                        elif ext in ["jpg", "png"]:
                            st.image(path)

                    st.divider()

            else:
                st.info("No materials uploaded yet")

        else:
            st.warning("No materials file found")

    # ===============================
    # 📸 TEST ATTENTION
    # ===============================
    elif menu == "📸 Test Attention":

        st.header("📸 Test Attention")

        course = st.text_input("Course", key="test_course")
        subject = st.text_input("Subject", key="test_subject")

        img = st.camera_input("Capture")

        if img and st.button("Analyze", key="analyze_btn"):
            image = Image.open(img)
            tag, prob = local_predict(image)

            st.success(f"{tag} ({prob * 100:.2f}%)")

            with open("attendance.csv", "a", newline="") as f:
                csv.writer(f).writerow([
                    datetime.now().strftime("%Y-%m-%d"),
                    datetime.now().strftime("%H:%M:%S"),
                    course,
                    subject,
                    st.session_state.user["username"],
                    tag,
                    prob
                ])

    # ===============================
    # 📝 ATTENDANCE
    # ===============================
    elif menu == "📝 Attendance":

        st.header("📝 Attendance Records")

        if os.path.exists("attendance.csv"):

            rows = list(csv.reader(open("attendance.csv")))
            clean_rows = []

            for r in rows:
                if len(r) >= 7:
                    try:
                        clean_rows.append([
                            r[0], r[1], r[2], r[3], r[4], r[5],
                            f"{float(r[6]) * 100:.2f}%"
                        ])
                    except:
                        continue

            if clean_rows:
                st.table(
                    [["Date", "Time", "Course", "Subject", "User", "Status", "Confidence"]]
                    + clean_rows
                )
            else:
                st.warning("No valid attendance data found")

    # ===============================
    # 👤 PROFILE
    # ===============================
    elif menu == "👤 My Profile":

        st.header("👤 Teacher Profile")

        u = st.session_state.user

        col1, col2 = st.columns([1, 2])

        with col1:
            st.image(u["photo"], width=200)

            new_photo = st.file_uploader(
                "Change Photo",
                ["jpg", "png"],
                key="profile_photo"
            )

            if new_photo:
                os.makedirs("teacher_photos", exist_ok=True)
                path = f"teacher_photos/{u['username']}.jpg"

                with open(path, "wb") as f:
                    f.write(new_photo.getbuffer())

                u["photo"] = path
                st.success("✅ Photo Updated")
                st.rerun()

        with col2:
            with st.form("edit_profile"):
                name = st.text_input("Name", u["name"], key="profile_name")
                email = st.text_input("Email", u["email"], key="profile_email")
                phone = st.text_input("Phone", u["phone"], key="profile_phone")

                save = st.form_submit_button("Save Changes")

                if save:
                    updated = update_user_profile(
                        "teachers.csv",
                        u["username"],
                        name,
                        email,
                        phone,
                        u["photo"]
                    )

                    if updated:
                        st.session_state.user.update({
                            "name": updated[1],
                            "email": updated[2],
                            "phone": updated[3],
                            "photo": updated[5]
                        })
                        st.success("Profile Updated")
                        st.rerun()

        st.divider()
        st.subheader("🔒 Change Password")

        with st.form("change_pass"):
            old_pass = st.text_input(
                "Old Password",
                type="password",
                key="teacher_old_pass"
            )
            new_pass = st.text_input(
                "New Password",
                type="password",
                key="teacher_new_pass"
            )

            change = st.form_submit_button("Update Password")

            if change:
                rows = []
                updated_flag = False

                with open("teachers.csv", "r") as f:
                    for r in csv.reader(f):
                        if r[0] == u["username"] and r[4] == hash_password(old_pass):
                            r[4] = hash_password(new_pass)
                            updated_flag = True
                        rows.append(r)

                with open("teachers.csv", "w", newline="") as f:
                    csv.writer(f).writerows(rows)

                if updated_flag:
                    st.success("Password Changed")
                else:
                    st.error("Wrong Old Password")
# ===============================
# 🎓 STUDENT (ENHANCED FINAL)
# ===============================
if st.session_state.role == "student":

    menu = st.sidebar.radio(
        "Navigation",
        ["🏠 Home", "📸 Study Monitoring", "📊 My Attendance", "📂 Teacher Materials", "👤 My Profile"]
    )

    # ===============================
    # 🏠 HOME DASHBOARD
    # ===============================
    if menu == "🏠 Home":

        st.title("🎓 Student Dashboard")

        st.subheader("📂 Upload Homework")

        hw_file = st.file_uploader(
            "Upload Homework (PDF/Image)",
            type=["pdf", "jpg", "png"],
            key="student_hw"
        )

        if hw_file:
            os.makedirs("student_hw", exist_ok=True)

            path = f"student_hw/{st.session_state.user['username']}_{hw_file.name}"

            with open(path, "wb") as f:
                f.write(hw_file.getbuffer())

            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with open("homework.csv", "a", newline="") as f:
                csv.writer(f).writerow([
                    date,
                    st.session_state.user["username"],
                    hw_file.name,
                    path
                ])

            st.success("✅ Homework Uploaded")

        st.divider()

        # -------- SHOW STUDENT UPLOADED HW --------
        st.subheader("📑 My Submitted Homework")

        if os.path.exists("homework.csv"):

            rows = list(csv.reader(open("homework.csv")))

            for i, r in enumerate(rows[::-1]):

                if len(r) < 4:
                    continue

                date, user, filename, path = r

                if user != st.session_state.user["username"]:
                    continue

                c1, c2 = st.columns([3,1])

                c1.write(f"📅 {date} - {filename}")

                if c2.button("View", key=f"hw_{i}"):

                    ext = path.split(".")[-1]

                    if ext == "pdf":
                        with open(path, "rb") as f:
                            st.download_button(
                                "Download",
                                f,
                                file_name=filename,
                                key=f"hw_pdf_{i}"
                            )
                    else:
                        st.image(path)

    # ===============================
    # 📸 STUDY MONITORING (UNCHANGED)
    # ===============================
    elif menu == "📸 Study Monitoring":

        img = st.camera_input("Capture Image")

        if img and st.button("Analyze"):
            image = Image.open(img)
            tag, prob = local_predict(image)
            prob = round(prob * 100, 2)

            if tag == "Focused":
                st.success(f"Focused ({prob}%)")
            elif tag == "Looking_Away":
                st.warning(f"Looking Away ({prob}%)")
            else:
                st.error(f"Sleeping ({prob}%)")

    # ===============================
    # 📊 ATTENDANCE (UNCHANGED)
    # ===============================
    elif menu == "📊 My Attendance":

        if os.path.exists("attendance.csv"):
            st.dataframe(list(csv.reader(open("attendance.csv"))))

    # ===============================
    # 📂 TEACHER MATERIALS (NEW)
    # ===============================
    elif menu == "📂 Teacher Materials":

        st.title("📂 Teacher Uploaded Materials")

        if os.path.exists("materials.csv"):

            rows = list(csv.reader(open("materials.csv")))

            for i, r in enumerate(rows[::-1]):

                if len(r) < 5:
                    continue

                date, course, subject, filename, path = r

                c1, c2, c3, c4 = st.columns([2,2,2,1])

                c1.write(f"📅 {date}")
                c2.write(f"📘 {course}")
                c3.write(f"📖 {subject}")

                if c4.button("Open", key=f"student_mat_{i}"):

                    ext = path.split(".")[-1]

                    if ext == "pdf":
                        with open(path, "rb") as f:
                            st.download_button(
                                "Download PDF",
                                f,
                                file_name=filename,
                                key=f"mat_pdf_{i}"
                            )

                    elif ext == "mp4":
                        st.video(path)

                    elif ext in ["jpg", "png"]:
                        st.image(path)

    # ===============================
    # 👤 PROFILE (ENHANCED)
    # ===============================
    elif menu == "👤 My Profile":

        st.header("👤 Student Profile")

        u = st.session_state.user

        col1, col2 = st.columns([1,2])

        # -------- PHOTO --------
        with col1:
            st.image(u["photo"], width=200)

            new_photo = st.file_uploader(
                "Change Photo",
                ["jpg", "png"],
                key="student_photo"
            )

            if new_photo:
                os.makedirs("student_photos", exist_ok=True)
                path = f"student_photos/{u['username']}.jpg"

                with open(path, "wb") as f:
                    f.write(new_photo.getbuffer())

                u["photo"] = path
                st.success("✅ Photo Updated")
                st.rerun()

        # -------- EDIT PROFILE --------
        with col2:
            with st.form("student_profile"):

                name = st.text_input("Name", u["name"], key="student_name")
                email = st.text_input("Email", u["email"], key="student_email")
                phone = st.text_input("Phone", u["phone"], key="student_phone")

                save = st.form_submit_button("Save Changes")

                if save:
                    updated = update_user_profile(
                        "students.csv",
                        u["username"],
                        name,
                        email,
                        phone,
                        u["photo"]
                    )

                    if updated:
                        st.session_state.user.update({
                            "name": updated[1],
                            "email": updated[2],
                            "phone": updated[3],
                            "photo": updated[5]
                        })
                        st.success("Profile Updated")
                        st.rerun()

        st.divider()

        # -------- CHANGE PASSWORD --------
        st.subheader("🔒 Change Password")

        with st.form("student_pass"):

            old_pass = st.text_input("Old Password", type="password", key="student_old")
            new_pass = st.text_input("New Password", type="password", key="student_new")

            change = st.form_submit_button("Update Password")

            if change:
                rows = []
                updated_flag = False

                with open("students.csv", "r") as f:
                    for r in csv.reader(f):
                        if r[0] == u["username"] and r[4] == hash_password(old_pass):
                            r[4] = hash_password(new_pass)
                            updated_flag = True
                        rows.append(r)

                with open("students.csv", "w", newline="") as f:
                    csv.writer(f).writerows(rows)

                if updated_flag:
                    st.success("Password Changed")
                else:
                    st.error("Wrong Old Password")