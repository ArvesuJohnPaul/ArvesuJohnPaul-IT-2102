import customtkinter as ctk
import mysql.connector
from tkinter import messagebox
import hashlib
import subprocess
import sys
from PIL import Image
from customtkinter import CTkImage
import json

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

class LoginSignupApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Login or Signup")
        self.master.geometry("800x600")

        # Create custom title bar
        self.title_bar = ctk.CTkFrame(self.master, height=40, corner_radius=0, fg_color="#663a82")
        self.title_bar.pack(fill='x', side='top')
        self.title_bar.pack_propagate(False)

        # Add app title/logo text
        self.title_label = ctk.CTkLabel(
            self.title_bar,
            text="ShopNGo",
            font=("Arial", 20, "bold"),
            text_color="white"
        )
        self.title_label.place(relx=0.5, rely=0.5, anchor="center")

        # Add exit button
        self.exit_button = ctk.CTkButton(
            self.title_bar,
            text="×",
            width=40,
            height=40,
            corner_radius=0,
            fg_color="#663a82",
            hover_color="#8b4daf",
            font=("Arial", 20),
            command=self.master.destroy
        )
        self.exit_button.pack(side='right')

        # Make window draggable
        self.title_bar.bind("<Button-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.on_move)

        # Load background image
        bg_image = Image.open("img/login_bg5.png")
        bg_image = bg_image.resize((500, 500), Image.Resampling.LANCZOS)

        self.bg_image = CTkImage(bg_image, size=(815, 620))
        self.bg_label = ctk.CTkLabel(self.master, image=self.bg_image, text="")
        self.bg_label.place(x=0, y=40, relwidth=1, relheight=1)

        #frame for login/sign-up
        self.frame = ctk.CTkFrame(self.master, width=800, height=1000, corner_radius=0, fg_color="white")
        self.frame.place(relx=0.69, rely=0.5, anchor="e")

        self.login_widgets()

    def connect_to_database(self):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="store_data"
            )
            cursor = conn.cursor()
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS store_data")
            cursor.execute("USE store_data")
            # Create user_login table if it doesn't exist
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_login (
                User_ID INT AUTO_INCREMENT PRIMARY KEY,
                U_Username VARCHAR(50) UNIQUE NOT NULL,
                U_Password VARCHAR(64) NOT NULL
            )
            """)
            conn.commit()
            return conn
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Could not connect to or create database: {e}")
            return None

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.master.winfo_x() + deltax
        y = self.master.winfo_y() + deltay
        self.master.geometry(f"+{x}+{y}")

    def login_widgets(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.frame, text="Welcome!", font=("Arial", 24, "bold"), text_color="black").pack(pady=0)

        ctk.CTkLabel(self.frame, text="Username", font=("Arial", 14), text_color="black").pack(pady=(10, 0))
        self.username_entry = ctk.CTkEntry(self.frame, width=300)
        self.username_entry.pack(pady=5)

        ctk.CTkLabel(self.frame, text="Password", font=("Arial", 14), text_color="black").pack(pady=(10, 0))
        self.password_entry = ctk.CTkEntry(self.frame, width=300, show="*")
        self.password_entry.pack(pady=5)

        ctk.CTkButton(self.frame, text="Login", command=self.login, width=150, fg_color="#FFA500").pack(pady=(20, 10))
        ctk.CTkButton(self.frame, text="Sign Up", command=self.signup_widgets, width=150, fg_color="#663a82",
                      text_color="white").pack()

        self.master.bind("<Return>", self.trigger_login)

    def trigger_login(self, event=None):
        self.login()

    def signup_widgets(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.frame, text="Sign Up", font=("Arial", 24, "bold"), text_color="black").pack(pady=20)

        ctk.CTkLabel(self.frame, text="Username", font=("Arial", 14), text_color="black").pack(pady=(10, 0))
        self.username_entry = ctk.CTkEntry(self.frame, width=300)
        self.username_entry.pack(pady=5)

        ctk.CTkLabel(self.frame, text="Password", font=("Arial", 14), text_color="black").pack(pady=(10, 0))
        self.password_entry = ctk.CTkEntry(self.frame, width=300, show="*")
        self.password_entry.pack(pady=5)

        ctk.CTkButton(self.frame, text="Sign Up", command=self.signup, width=150, fg_color="#FFA500").pack(
            pady=(20, 10))
        ctk.CTkButton(self.frame, text="Back to Login", command=self.login_widgets, width=150, fg_color="#663a82",
                      text_color="white").pack()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        hashed_password = hash_password(password)

        if not username or not password:
            messagebox.showerror("Input Error", "Please fill in all fields.")
            return

        conn = self.connect_to_database()
        if conn:
            cursor = conn.cursor()
            query = "SELECT User_ID FROM user_login WHERE U_Username = %s AND U_Password = %s"
            cursor.execute(query, (username, hashed_password))
            result = cursor.fetchone()
            conn.close()

            if result:
                user_id = result[0]
                login_data = {'user_id': user_id,
                              'username': username
                              }
                with open('login.json', 'w') as f:
                    json.dump(login_data, f)

                self.master.destroy()
                subprocess.Popen([sys.executable, "main.py"])
            else:
                messagebox.showerror("Login Failed", "Invalid username or password.")

    def signup(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        hashed_password = hash_password(password)

        if not username or not password:
            messagebox.showerror("Input Error", "Please fill in all fields.")
            return

        conn = self.connect_to_database()
        if conn:
            cursor = conn.cursor()
            try:
                query = "INSERT INTO user_login (U_Username, U_Password) VALUES (%s, %s)"
                cursor.execute(query, (username, hashed_password))
                conn.commit()
                messagebox.showinfo("Success", "Signup successful! Please login.")
                self.login_widgets()
            except mysql.connector.Error as e:
                if e.errno == 1062:
                    messagebox.showerror("Signup Failed", "Username already exists.")
                else:
                    messagebox.showerror("Database Error", f"Error: {e}")
            finally:
                conn.close()


if __name__ == "__main__":
    root = ctk.CTk()
    app = LoginSignupApp(root)
    root.mainloop()