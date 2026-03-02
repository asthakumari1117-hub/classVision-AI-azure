🎓 ClassVision AI – Classroom Attention Monitoring System

ClassVision AI is an AI-powered classroom attention monitoring web application built using Streamlit and Azure Custom Vision.
The app analyzes student attention from images and records attendance automatically.
To keep the application running 24/7, it is deployed on an Azure Virtual Machine.


🚀 Features

👩‍🏫 Teacher
Login & Signup
Start attention monitoring sessions
Capture image or upload image
Analyze student attention using AI
Automatic attendance recording
View & filter attendance records
Download attendance report (CSV)
Edit teacher profile


🎓 Student
Login & Signup
Study monitoring using camera or image upload
Attention prediction (Focused / Looking Away / Sleeping)
Automatic attendance saving
View personal attendance history
Study score calculation
Edit student profile


🧠 AI Model
Trained using Azure Custom Vision
Attention classes
Focused
Looking_Away
Sleeping
Integrated using Azure Prediction REST API


☁️ Azure Virtual Machine Deployment

Initially, the app was running only while the local terminal was open.
After closing the terminal, the application stopped.

To solve this problem, the application was deployed on an Azure Virtual Machine.

Why Azure VM?

App remains live even after system shutdown
Accessible using a public IP
Suitable for real-time deployment
Works independently of local system
A system service (systemd) is configured so the app automatically starts when the VM boots.


▶️ Run the Application
🖥️ Run Locally (Without Azure)

If the Azure subscription ends, the app can still be run locally:

git clone https://github.com/asthakumari1117-hub/classVision-AI-azure.git
cd classVision-AI-azure
pip install -r requirements.txt
streamlit run app.py

App will run at:

http://localhost:8501

⚠️ Note:
The app will stop when the terminal is closed.


☁️ Run on Azure VM (Live)

The app is deployed on an Azure Ubuntu VM and runs continuously using a system service.
Example:
http://<VM_PUBLIC_IP>:8501


🛠️ Technologies Used

Python
Streamlit
Azure Custom Vision
Azure Virtual Machine (Ubuntu)
systemd
CSV file storage


👩‍💻 Author

Astha Kumari
