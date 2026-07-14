import tkinter as tk
import re
from tkinter import messagebox
from database import add_customer
from ui_background import apply_window_background, style_on_background


def open_customer_window():

    email_pattern = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

    window = tk.Toplevel()
    window.title("Create Customer")
    window.geometry("900x600")
    apply_window_background(window)

    label_name = tk.Label(window, text="Customer Name")
    style_on_background(label_name)
    label_name.pack(pady=(40, 0))
    entry_name = tk.Entry(window)
    style_on_background(entry_name)
    entry_name.pack()

    label_cin = tk.Label(window, text="CIN")
    style_on_background(label_cin)
    label_cin.pack()
    entry_cin = tk.Entry(window)
    style_on_background(entry_cin)
    entry_cin.pack()

    label_email = tk.Label(window, text="Email")
    style_on_background(label_email)
    label_email.pack()
    entry_email = tk.Entry(window)
    style_on_background(entry_email)
    entry_email.pack()

    def save():

        name = entry_name.get().strip()
        cin = entry_cin.get().strip()
        email = entry_email.get().strip()

        if not name or not cin or not email:
            messagebox.showerror("Error", "All fields are required")
            return

        if len(name) < 3:
            messagebox.showerror("Error", "Name must contain at least 3 characters")
            return

        if not cin.isdigit() or len(cin) != 8:
            messagebox.showerror("Error", "Invalid CIN")
            return

        if not email_pattern.fullmatch(email):
            messagebox.showerror("Error", "Invalid email format")
            return

        success = add_customer(name, cin, email)

        if success:
            messagebox.showinfo("Success", "Customer added successfully")

            entry_name.delete(0, tk.END)
            entry_cin.delete(0, tk.END)
            entry_email.delete(0, tk.END)

            entry_name.focus()

        else:
            messagebox.showerror("Error", "CIN already exists")

    btn_save = tk.Button(window, text="Save Customer", command=save)
    style_on_background(btn_save)
    btn_save.pack(pady=10)
