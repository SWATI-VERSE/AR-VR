# 🎯 AI-Based Smart Attendance System with Liveness Detection

An intelligent, real-time attendance system that uses **Face Recognition + Liveness Detection** to ensure secure and spoof-proof attendance marking.

---

## 🚀 Overview

Traditional attendance systems are vulnerable to proxy attendance using photos or videos.  
This project solves that problem by integrating **AI-powered face recognition with liveness detection techniques** such as:

- 👁️ Blink Detection  
- ↔️ Head Movement Detection  
- ⏱️ Time-Based Presence Verification  

This ensures that only **real, physically present individuals** are marked for attendance.

---

## ✨ Key Features

- 🎥 Real-time Face Recognition
- 🔐 Anti-Spoofing (Liveness Detection)
- 👁️ Blink Detection using Eye Aspect Ratio (EAR)
- ↔️ Head Movement Challenge (Turn Left / Right)
- ⏳ Minimum Presence Duration Validation
- 🧠 Intelligent Verification System
- 📊 Automatic Attendance Logging (CSV)
- 📈 Export Attendance to Excel
- 🖥️ GUI Dashboard (Tkinter)
- 🔊 Voice Feedback for Verification
- ⚡ Fast & Efficient Processing

---

## 🧠 Tech Stack

| Technology | Purpose |
|----------|--------|
| Python | Core Programming |
| OpenCV | Image Processing |
| face_recognition | Face Encoding & Matching |
| dlib | Facial Landmark Detection |
| NumPy | Numerical Operations |
| Tkinter | GUI Dashboard |
| Pandas | Data Handling & Excel Export |
| pyttsx3 | Voice Feedback |

---

## 📂 Project Structure

```bash
SMART_ATTENDANCE_SYSTEM/
│
├── src/                          # Core system logic
│   ├── attendance_system_prod.py
│   ├── encode_faces.py
│   ├── capture_faces.py
│
├── DATASET/                      # Stored images of users
│
├── ENCODINGS/                    # Encoded face data
│   └── encodings.pickle
│
├── MODELS/                       # Pre-trained models
│   └── shape_predictor_68_face_landmarks.dat
│
├── ATTENDANCE/                  # Attendance records
│   ├── attendance.csv
│   └── attendance.xlsx
│
├── main_app.py                   # GUI dashboard (entry point)
├── requirements.txt              # Dependencies
├── README.md                     # Project documentation
├── .gitignore                    # Ignored files (venv, cache, etc.)

```
---

## ⚙️ Installation & Setup

```bash
### 1️⃣ Clone the Repository
git clone https://github.com/your-username/smart-attendance-system.git
cd smart-attendance-system

### 2️⃣ Install Dependencies
pip install -r requirements.txt

### 3️⃣ Run the Application
python main_app.py

```

---

🖥️ How It Works

1. User logs into the system
2. Starts attendance from dashboard
3. System detects face using camera
4. Performs **liveness checks**:
        Blink detection
        Head movement verification
        Time-based validation
5. If verified:
        Attendance is marked
        Voice confirmation is given
6. Data is stored in CSV and can be exported to Excel

---

🔍 Challenges Faced

        1. Handling real-time face recognition efficiently
        2. Improving accuracy under different lighting conditions
        3. Tuning blink detection thresholds
        4. Synchronizing multiple liveness checks

---

🚀 Future Enhancements

        ☁️ Cloud-based attendance storage
        📱 Mobile application integration
        😷 Mask detection support
        📡 Multi-camera support for large classrooms
        🔐 Face anti-spoofing using deep learning

---

📌 Use Cases

        1.Educational Institutions
        2.Corporate Offices
        3.Secure Entry Systems
        4.Examination Centers

---

👩‍💻 AUTHORS

    1. Swati Parida
    2. Arpita Priyadarshini Acharya

---

⭐ Conclusion

This project demonstrates how combining Face Recognition with Liveness Detection can significantly enhance the reliability and security of attendance systems.

---