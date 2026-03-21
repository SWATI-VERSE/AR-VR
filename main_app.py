import cv2
import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

# ================= LOGIN FUNCTION =================
def login():
    username = entry_user.get()
    password = entry_pass.get()

    if username == "admin" and password == "1234":
        messagebox.showinfo("Login", "Login Successful!")
        open_dashboard()
    else:
        messagebox.showerror("Login", "Invalid Credentials")

# ================= DASHBOARD =================
def open_dashboard():
    login_window.destroy()

    dashboard = tk.Tk()
    dashboard.title("Attendance Dashboard")
    dashboard.geometry("400x300")

    tk.Label(dashboard, text="Dashboard", font=("Arial", 18)).pack(pady=20)

    tk.Button(dashboard, text="Start Attendance",
              width=20, height=2,
              command=start_attendance).pack(pady=10)

    tk.Button(dashboard, text="View Attendance",
              width=20, height=2,
              command=view_attendance).pack(pady=10)

    tk.Button(dashboard, text="Exit",
              width=20, height=2,
              command=dashboard.destroy).pack(pady=10)

    dashboard.mainloop()

# ================= START CAMERA =================
def start_attendance():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(base_dir, "src", "attendance_system_prod.py")

    subprocess.run([sys.executable, script_path])


# ================= VIEW CSV =================
def view_attendance():
    file_path = os.path.join("ATTENDANCE", "attendance.csv")

    if os.path.exists(file_path):
        os.startfile(file_path)  # Windows
    else:
        messagebox.showerror("Error", "No attendance file found")

# ================= LOGIN UI =================
login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("300x250")

tk.Label(login_window, text="Login System", font=("Arial", 16)).pack(pady=15)

tk.Label(login_window, text="Username").pack()
entry_user = tk.Entry(login_window)
entry_user.pack()

tk.Label(login_window, text="Password").pack()
entry_pass = tk.Entry(login_window, show="*")
entry_pass.pack()

tk.Button(login_window, text="Login",
          width=15, command=login).pack(pady=20)

login_window.mainloop()
