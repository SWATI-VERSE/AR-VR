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

    if username == "SWATI" and password == "12345":
        messagebox.showinfo("Login", "Login Successful!")
        open_dashboard()
    else:
        messagebox.showerror("Login", "Invalid Credentials")


# ================= DASHBOARD =================
def open_dashboard():
    login_window.destroy()

    dashboard = tk.Tk()
    dashboard.title("Attendance Dashboard")
    dashboard.geometry("420x420")
    dashboard.configure(bg="lavender")

    def styled_button(text, command):
        return tk.Button(
            dashboard,
            text=text,
            command=command,
            font=("Segoe UI", 11, "bold"),
            bg="lightblue",
            fg="black",
            activebackground="powderblue",
            relief="flat",
            bd=0,
            padx=10,
            pady=8,
            width=25
        )

    tk.Label(
        dashboard,
        text="Attendance Dashboard",
        font=("Segoe UI", 18, "bold"),
        bg="lavender",
        fg="slategray"
    ).pack(pady=20)

    styled_button("Start Attendance", start_attendance).pack(pady=10)
    styled_button("Add New Student", add_student).pack(pady=10)
    styled_button("View Attendance", view_attendance).pack(pady=10)
    styled_button("Export to Excel", export_excel).pack(pady=10)
    styled_button("Exit", dashboard.destroy).pack(pady=10)

    dashboard.mainloop()


# ================= ADD STUDENT =================
def add_student():
    add_window = tk.Toplevel()
    add_window.title("Add New Student")
    add_window.geometry("300x200")

    tk.Label(add_window, text="Enter Student Name").pack(pady=10)

    name_entry = tk.Entry(add_window)
    name_entry.pack(pady=5)

    def capture_and_encode():
        name = name_entry.get()   # ✅ FIXED

        if name.strip() == "":
            messagebox.showerror("Error", "Enter student name")
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))

        capture_path = os.path.join(base_dir, "src", "capture_faces.py")
        encode_path = os.path.join(base_dir, "src", "encode_faces.py")

        # Step 1: Capture images
        subprocess.run([sys.executable, capture_path, name])

        # Step 2: Encode faces
        subprocess.run([sys.executable, encode_path])

        messagebox.showinfo("Success", f"{name} added successfully!")

    tk.Button(add_window, text="Start Capture",
              command=capture_and_encode).pack(pady=20)


# ================= START ATTENDANCE =================
def start_attendance():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(base_dir, "src", "attendance_system_prod.py")

    subprocess.run([sys.executable, script_path])


# ================= VIEW CSV =================
def view_attendance():
    file_path = os.path.join("ATTENDANCE", "attendance.csv")

    if not os.path.exists(file_path):
        messagebox.showerror("Error", "No Attendance file found")
        return

    view_window = tk.Toplevel()
    view_window.title("Attendance Records")
    view_window.geometry("500x400")

    text = tk.Text(view_window)
    text.pack(fill="both", expand=True)

    with open(file_path, "r") as f:
        text.insert(tk.END, f.read())


# ================= EXPORT TO EXCEL =================
def export_excel():
    import pandas as pd
    import os

    file_path = os.path.join("ATTENDANCE", "attendance.csv")

    if not os.path.exists(file_path):
        messagebox.showerror("Error", "No Attendance File Found")
        return

    df = pd.read_csv(file_path)
    excel_path = os.path.join("ATTENDANCE", "attendance.xlsx")
    df.to_excel(excel_path, index=False)

    os.startfile(excel_path) # Auto open file

    messagebox.showinfo("Success", "Exported and opened successfully!")

# ================= LOGIN UI =================

login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("320x300")
login_window.configure(bg="lavender")

tk.Label(
    login_window,
    text="Login System",
    font=("Segoe UI", 18, "bold"),
    bg="lavender",
    fg="slategray"
).pack(pady=20)

tk.Label(login_window, text="Username", bg="lavender", fg="gray").pack()
entry_user = tk.Entry(login_window)
entry_user.pack(pady=5)

tk.Label(login_window, text="Password", bg="lavender", fg="gray").pack()
entry_pass = tk.Entry(login_window, show="*")
entry_pass.pack(pady=5)

tk.Button(
    login_window,
    text="Login",
    command=login,
    font=("Segoe UI", 11, "bold"),
    bg="lightblue",
    fg="black",
    activebackground="powderblue",
    relief="flat",
    width=15,
    pady=6
).pack(pady=20)

login_window.mainloop()
