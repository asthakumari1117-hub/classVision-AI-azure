# 🎓 ClassVision AI – Classroom Attention Monitoring System

ClassVision AI is an **AI-powered classroom attention monitoring web application** built using **Streamlit** and **Azure Custom Vision**.  
The application analyzes student attention from images and **automatically records attendance**.

The project demonstrates **end-to-end AI + Cloud deployment**, including:
- AI model training
- Web application development
- 24/7 deployment using cloud infrastructure
- CI/CD via GitHub

---

## 🚀 Live Demo

🔗 **Streamlit Cloud (Current Deployment):**  
https://classvision-ai-azure-xvws22afcwdp3ze3gcuwba.streamlit.app/

> The app is currently deployed on **Streamlit Cloud**, which automatically redeploys the latest code on every GitHub push.

---

🛠️ Technologies Used

Programming Language

Python

Web Framework

Streamlit

AI / Machine Learning

Azure Custom Vision

Cloud & Deployment

Azure Virtual Machine (Ubuntu)

Streamlit Cloud

Backend & System

REST APIs

systemd (Linux service for auto-start)

Data Storage

CSV File Storage

Version Control & CI/CD

Git

GitHub (CI/CD)

## 🚀 Features

### 👩‍🏫 Teacher Module
- Login & Signup
- Start attention monitoring sessions
- Capture image using camera or upload image
- Analyze student attention using AI
- Automatic attendance recording
- View and filter attendance records
- Download attendance reports (CSV)
- Edit teacher profile

---

### 🎓 Student Module
- Login & Signup
- Study monitoring using camera or image upload
- Attention prediction:
  - Focused
  - Looking Away
  - Sleeping
- Automatic attendance saving
- View personal attendance history
- Study score calculation
- Edit student profile

---

## 🧠 AI Model

- Trained using **Azure Custom Vision**
- Attention classification categories:
  - Focused
  - Looking_Away
  - Sleeping
- Integrated into the app using **Azure Custom Vision Prediction REST API**

---

## ☁️ Cloud Deployment Journey

### 🔹 Initial Deployment (Azure Virtual Machine)

Initially, the application could run **only while the local terminal was open**.  
Closing the terminal would stop the application.

To solve this, the app was deployed on an **Azure Ubuntu Virtual Machine**.

#### Why Azure VM?
- App runs **24/7**, even after system shutdown
- Accessible via **public IP**
- Independent of local machine
- Suitable for real-time AI applications
- **systemd service** configured so the app auto-starts when the VM boots

Example: http://<VM_PUBLIC_IP>:8501


---

### 🔹 Current Deployment (Streamlit Cloud)

After the Azure subscription ended, the application was migrated to **Streamlit Cloud**.

#### Benefits of Streamlit Cloud:
- No VM or billing required
- Automatic deployment from GitHub
- App stays live even when:
  - Laptop is off
  - VS Code is closed
- Ideal for demos, portfolios, and interviews

Live App: https://classvision-ai-azure-xvws22afcwdp3ze3gcuwba.streamlit.app/


---

## ▶️ Run the Application Locally

If the cloud deployment is unavailable, the app can be run locally.

### 🖥️ Local Setup

```bash
git clone https://github.com/asthakumari1117-hub/classVision-AI-azure.git
cd classVision-AI-azure
pip install -r requirements.txt
streamlit run app.py

