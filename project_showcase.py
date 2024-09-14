import sqlite3
import re
from tkinter import messagebox
from customtkinter import *


# Initialize the main application window
app = CTk()
app.geometry("500x400")
set_appearance_mode("dark")
set_default_color_theme("dark-blue")
app.title("Dhaka Stock Exchange")

# Global variables
frame = None

# Database connection
def connect_to_database():
    try:
        conn = sqlite3.connect('stock_market.db')
        return conn
    except Exception as e:
        print(f"Failed to connect to the database: {str(e)}")
        exit()

connection = connect_to_database()
cursor = connection.cursor()

# User authentication and registration
def login_check(phone_number, password):
    sql = "SELECT user_id FROM users WHERE phone_number = ? AND password = ?"
    cursor.execute(sql, (phone_number, password))
    result = cursor.fetchone()
    if result:
        show_main_page(result[0])
    else:
        messagebox.showerror("Error", "Invalid Credentials")


def register_user(full_name, nid_number, phone_number, password):
    if not re.match(r'^\d{12}$', nid_number):
        messagebox.showerror("Error", "NID number must be exactly 12 digits")
        return
    if not re.match(r'^\d{11}$', phone_number):
        messagebox.showerror("Error", "Phone number must be exactly 11 digits")
        return

    try:
        sql = "INSERT INTO users (full_name, nid_number, phone_number, password) VALUES (?, ?, ?, ?)"
        cursor.execute(sql, (full_name, nid_number, phone_number, password))
        connection.commit()
        messagebox.showinfo("Success", "Registration successful")
        show_login_page()
    except sqlite3.IntegrityError as e:
        if "nid_number" in str(e):
            messagebox.showerror("Error", "NID number already exists")
        elif "phone_number" in str(e):
            messagebox.showerror("Error", "Phone number already exists")
        else:
            messagebox.showerror("Error", "Registration failed")
# User interface functions
def clear_frame():
    for widget in frame.winfo_children():
        widget.destroy()

def show_login_page():
    global frame
    clear_frame()

    phone_entry = CTkEntry(master=frame, placeholder_text="Phone Number")
    phone_entry.pack(pady=10)

    password_entry = CTkEntry(master=frame, placeholder_text="Password", show="*")
    password_entry.pack(pady=10)

    login_button = CTkButton(master=frame, text="Login", fg_color="#40e0d0", hover_color="#32cd32",
                             command=lambda: login_check(phone_entry.get(), password_entry.get()))
    login_button.pack(pady=10)

    signup_button = CTkButton(master=frame, text="Sign Up", fg_color="#40e0d0", hover_color="#32cd32",
                              command=show_signup_page)
    signup_button.pack(pady=10)

def show_signup_page():
    global frame
    clear_frame()

    name_entry = CTkEntry(master=frame, placeholder_text="Full Name")
    name_entry.pack(pady=10)

    nid_entry = CTkEntry(master=frame, placeholder_text="NID Number (12 digits)")
    nid_entry.pack(pady=10)

    phone_entry = CTkEntry(master=frame, placeholder_text="Phone Number (11 digits)")
    phone_entry.pack(pady=10)

    password_entry = CTkEntry(master=frame, placeholder_text="Password", show="*")
    password_entry.pack(pady=10)

    signup_button = CTkButton(master=frame, text="Sign Up", fg_color="#40e0d0", hover_color="#32cd32",
                              command=lambda: register_user(name_entry.get(), nid_entry.get(),
                                                            phone_entry.get(), password_entry.get()))
    signup_button.pack(pady=10)

    back_button = CTkButton(master=frame, text="Back to Login", fg_color="#40e0d0", hover_color="#32cd32",
                            command=show_login_page)
    back_button.pack(pady=10)

def show_main_page(user_id):
    global frame
    clear_frame()

    welcome_label = CTkLabel(master=frame, text=f"Welcome, User {user_id}!")
    welcome_label.pack(pady=20)

    # Placeholder for balance
    balance_label = CTkLabel(master=frame, text="Balance: ৳ 10000")
    balance_label.pack(pady=10)

    # Placeholder buttons for main functionalities
    portfolio_button = CTkButton(master=frame, text="View Portfolio", fg_color="#40e0d0", hover_color="#32cd32")
    portfolio_button.pack(pady=10)

    trade_button = CTkButton(master=frame, text="Trade Stocks", fg_color="#40e0d0", hover_color="#32cd32")
    trade_button.pack(pady=10)

    logout_button = CTkButton(master=frame, text="Logout", fg_color="#40e0d0", hover_color="#32cd32",
                              command=show_login_page)
    logout_button.pack(pady=10)

# Main
frame = CTkFrame(master=app, width=300, height=400)
frame.pack(padx=20, pady=20, fill="both", expand=True)

show_login_page()
app.mainloop()