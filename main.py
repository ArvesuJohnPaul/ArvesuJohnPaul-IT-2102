import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import json
from pathlib import Path
from tkinter import Listbox
from customtkinter import CTkImage
import subprocess
import sys
import mysql.connector
from datetime import datetime
import platform


cart_items = {}
store_data_file = 'store_data.json'


class GroceryStoreApp:
    def __init__(self, master):
        self.main_canvas = None
        self.selected_category = ctk.StringVar(value='All')
        #master.overrideredirect(True)
        master.geometry("1330x900")
        master.attributes('-fullscreen', False)  # ensure it's not fullscreen

        self.root = master
        self.store_data = self.load_store_data()
        self.store_images = {}
        self.load_store_images()
        self.cart_listbox = None
        self.username_entry = None
        self.password_entry = None
        self.db_connection = self.connect_to_database()
        self.cursor = self.db_connection.cursor()
        self.cart_listbox = Listbox(self.root)
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.offset_x = 0
        self.offset_y = 0
        self.check_user()

        # Navigation Bar
        navbar = ctk.CTkFrame(root, fg_color="#52307C", height=60, corner_radius=0)
        navbar.pack(side="top", fill="x")
        navbar.bind("<ButtonPress-1>", self.start_drag)
        navbar.bind("<B1-Motion>", self.dragging)
        navbar.bind("<ButtonRelease-1>", self.stop_drag)

        # Logo image
        try:
            cart_logo_path = 'img/cart_logo.png'
            cart_logo_image = Image.open(cart_logo_path).resize((70, 70), Image.Resampling.LANCZOS)
            cart_logo_ctk_image = CTkImage(cart_logo_image)
        except Exception as e:
            print(f"Failed to load cart logo: {e}")
            cart_logo_ctk_image = None

        # Add logo and text to the navbar
        if cart_logo_ctk_image:
            ctk.CTkLabel(navbar, image=cart_logo_ctk_image, text="").pack(side="left", padx=10)

        ctk.CTkLabel(navbar, text="ShopNGo", font=("Arial", 20, "bold"), text_color="White").pack(side="left", padx=10)

        # Add logged in user display in center
        try:
            with open('login.json', 'r') as f:
                login_data = json.load(f)
                username = login_data.get('username', 'Guest')
            user_label = ctk.CTkLabel(
                navbar,
                text=f"Welcome, {username}!",
                font=("Arial", 16),
                text_color="White"
            )
            user_label.place(relx=0.5, rely=0.5, anchor="center")
        except Exception as e:
            print(f"Failed to load user data: {e}")

        # Menu dropdown
        try:
            menu_logo_path = 'img/menu_logo.png'
            menu_logo_image = Image.open(menu_logo_path).resize((49, 49), Image.Resampling.LANCZOS)
            self.menu_logo_ctk_image = CTkImage(menu_logo_image)
        except Exception as e:
            print(f"Failed to load menu logo: {e}")
            self.menu_logo_ctk_image = None

        if self.menu_logo_ctk_image:
            self.menu_button = ctk.CTkButton(
                navbar,
                image=self.menu_logo_ctk_image,
                text="",
                width=50,
                height=50,
                fg_color="#52307C",
                hover_color="#7C5295",
                command=self.menu_dropdown
            )
            self.menu_button.pack(side="right", padx=10)
        self.dropdown_frame = None

        # Cart dropdown
        try:
            cart_logo_path = 'img/cart.png'
            cart_logo_image = Image.open(cart_logo_path).resize((49, 49), Image.Resampling.LANCZOS)
            self.cart_logo_ctk_image = CTkImage(cart_logo_image)
        except Exception as e:
            print(f"Failed to load cart logo: {e}")
            self.cart_logo_ctk_image = None

        if self.cart_logo_ctk_image:
            self.cart_button = ctk.CTkButton(
                navbar,
                image=self.cart_logo_ctk_image,
                text="",
                width=50,
                height=50,
                fg_color="#52307C",
                hover_color="#7C5295",
                command=self.cart_dropdown
            )
            self.cart_button.pack(side="right", padx=10)
        self.cart_dropdown_frame = None

        # Background Image
        try:
            bg_image_path = 'img/bg.png'
            self.bg_image = Image.open(bg_image_path).resize((1330, 910), Image.Resampling.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(self.bg_image)

            self.canvas = ctk.CTkCanvas(root, width=1800, height=900)
            self.canvas.pack(fill="both", expand=True)
            self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        except Exception as e:
            print(f"Failed to load background image: {e}")

        # Frames for Customer section
        self.customer_frame = ctk.CTkFrame(self.root, fg_color='white')
        self.customer_frame.place(x=105, y=125)
        self.customer_frame.configure(width=800, height=400)
        self.customer_section()
        self.update_cart_list()

    #checks the json file if there is someone logged in
    def check_user(self):
        try:
            with open('login.json', 'r') as f:
                login_data = json.load(f)
            if not login_data.get('user_id'):
                raise ValueError("No user is logged in.")
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            messagebox.showwarning("Login Required", "You need to log in first.")
            subprocess.Popen([sys.executable, "login.py"])
            sys.exit()

#=============================================Drag methods==================================================

    def start_drag(self, event):
        self.offset_x = event.x_root - self.root.winfo_x()
        self.offset_y = event.y_root - self.root.winfo_y()

    def dragging(self, event):
        x = event.x_root - self.offset_x
        y = event.y_root - self.offset_y
        self.root.geometry(f"+{x}+{y}")

    def stop_drag(self, event):
        pass

#=============================================database functions=============================================
    #database connection
    def connect_to_database(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="POPE",
                password="april435",
                database="store_data"
            )
            return connection
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error connecting to database: {err}")
            sys.exit(1)

    def update_database(self, item_name, quantity):
        #only updates quantity
        try:
            query = "UPDATE item_data SET quantity = %s WHERE item_name = %s"
            self.cursor.execute(query, (quantity, item_name))
            self.db_connection.commit()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error updating item quantity: {err}")

    def get_item_id(self, item_name):
        try:
            query = "SELECT Item_ID FROM item_data WHERE item_name = %s"
            self.cursor.execute(query, (item_name,))
            result = self.cursor.fetchone()

            if result:
                return result[0]
            else:
                messagebox.showerror("Error", f"Item {item_name} not found in database")
                return None
        except Exception as e:
            messagebox.showerror("Error", f"Error getting item ID: {e}")
            return None

    def db_receipt(self, user_id):
        #Create a new receipt entry for the db
        try:
            current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            total_price = self.calculate_total_price()

            query = """
            INSERT INTO receipt (User_ID, date, total_price)
            VALUES (%s, %s, %s)
            """
            self.cursor.execute(query, (user_id, current_date, total_price))
            self.db_connection.commit()

            return self.cursor.lastrowid
        except Exception as e:
            messagebox.showerror("Error", f"Error creating receipt: {e}")
            return None

    def db_receipt_items(self, receipt_id, user_id):
        #Create receipt_items entries for each item in the cart
        try:
            for item_name, quantity in cart_items.items():
                item_id = self.get_item_id(item_name)
                if item_id is None:
                    continue

                price = float(self.store_data[item_name]['price'].replace('₱', '').replace('$', ''))

                query = """
                INSERT INTO receipt_items (Receipt_ID, Item_ID, quantity, price)
                VALUES (%s, %s, %s, %s)
                """
                self.cursor.execute(query, (receipt_id, item_id, quantity, price))

            self.db_connection.commit()
        except Exception as e:
            messagebox.showerror("Error", f"Error creating receipt items: {e}")

#=============================================Frames & Windows=============================================

    def cart_dropdown(self):

        cart_is_visible = (
                hasattr(self, 'cart_dropdown_frame')
                and self.cart_dropdown_frame is not None
                and self.cart_dropdown_frame.winfo_exists()
        )

        if cart_is_visible:
            self.cart_dropdown_frame.destroy()
            self.cart_dropdown_frame = None
            return

        # Create new dropdown frame
        self.cart_dropdown_frame = ctk.CTkFrame(
            self.root,
            fg_color="#7C5295",
            corner_radius=10,
            width=250,
            height=500
        )
        self.cart_dropdown_frame.place(x=1050, y=60)
        self.cart_dropdown_frame.pack_propagate(False)
        self.cart_dropdown_frame.grid_propagate(False)

        # Cart Header
        ctk.CTkLabel(
            self.cart_dropdown_frame,
            text="Cart",
            font=("Arial", 16, "bold"),
            text_color="white"
        ).pack(pady=(10, 5))

        #Item Frame
        canvas_frame = ctk.CTkFrame(
            self.cart_dropdown_frame,
            fg_color="#52307C",
            width=300,
            height=320
        )
        canvas_frame.pack(padx=10, pady=5)
        canvas_frame.pack_propagate(False)
        canvas_frame.grid_propagate(False)

        canvas = tk.Canvas(
            canvas_frame,
            bg="#52307C",
            highlightthickness=0,
            width=300,
            height=400
        )
        scrollbar = ctk.CTkScrollbar(canvas_frame, orientation="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas, fg_color="#52307C", width=220)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=220)

        #Track selected item
        self.selected_cart_item = None
        self.cart_items_frames = []

        def select_item(item_name, frame):
            for f in self.cart_items_frames:
                f.configure(fg_color="#52307C")
            # Change color of item selected
            frame.configure(fg_color="#3B2359")
            self.selected_cart_item = item_name

        # Items images
        for item, quantity in cart_items.items():
            item_frame = ctk.CTkFrame(scrollable_frame, fg_color="#52307C", height=80)
            item_frame.pack(fill="x", padx=5, pady=2)
            item_frame.pack_propagate(False)
            item_frame.bind("<Button-1>", lambda e, name=item, frame=item_frame: select_item(name, frame))

            if 'image_path' in self.store_data[item]:
                try:
                    img = Image.open(self.store_data[item]['image_path'])
                    img = img.resize((60, 60), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)

                    image_label = tk.Label(
                        item_frame,
                        image=photo,
                        bg="#52307C",
                        borderwidth=0,
                        highlightthickness=0
                    )
                    image_label.image = photo
                    image_label.pack(side="left", padx=5)
                    image_label.bind("<Button-1>", lambda e, name=item, frame=item_frame: select_item(name, frame))
                except Exception as e:
                    print(f"Failed to load image for {item}: {e}")
                    empty_label = ctk.CTkLabel(item_frame, text="", width=60)
                    empty_label.pack(side="left", padx=5)

            # Item details frame
            details_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            details_frame.pack(side="left", fill="both", expand=True, padx=5)
            details_frame.bind("<Button-1>", lambda e, name=item, frame=item_frame: select_item(name, frame))

            # Item name and quantity
            name_label = ctk.CTkLabel(
                details_frame,
                text=f"{item}",
                font=("Arial", 12, "bold"),
                text_color="white"
            )
            name_label.pack(anchor="w")
            name_label.bind("<Button-1>", lambda e, name=item, frame=item_frame: select_item(name, frame))

            quantity_price_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
            quantity_price_frame.pack(fill="x")
            quantity_price_frame.bind("<Button-1>", lambda e, name=item, frame=item_frame: select_item(name, frame))

            qty_label = ctk.CTkLabel(
                quantity_price_frame,
                text=f"Qty: {quantity}",
                font=("Arial", 10),
                text_color="white"
            )
            qty_label.pack(side="left")
            qty_label.bind("<Button-1>", lambda e, name=item, frame=item_frame: select_item(name, frame))

            # Item price
            price = float(self.store_data[item]['price'].replace('₱', '').replace('$', ''))
            price_label = ctk.CTkLabel(
                quantity_price_frame,
                text=f"₱{price * quantity:.2f}",
                font=("Arial", 10),
                text_color="white"
            )
            price_label.pack(side="right")
            price_label.bind("<Button-1>", lambda e, name=item, frame=item_frame: select_item(name, frame))

            self.cart_items_frames.append(item_frame)

        scrollable_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        # Quantity Selector
        quantity_frame = ctk.CTkFrame(self.cart_dropdown_frame, fg_color="#7C5295")
        quantity_frame.pack(pady=5)

        self.quantity_to_remove = 1
        self.quantity_label = ctk.CTkLabel(
            quantity_frame,
            text=str(self.quantity_to_remove),
            font=("Arial", 16),
            text_color="white"
        )
        decrease_button = ctk.CTkButton(
            quantity_frame,
            text="-",
            width=30,
            fg_color="#52307C",
            command=self.decrease_quantity
        )
        increase_button = ctk.CTkButton(
            quantity_frame,
            text="+",
            width=30,
            fg_color="#52307C",
            command=self.increase_quantity
        )

        decrease_button.grid(row=0, column=0, padx=5)
        self.quantity_label.grid(row=0, column=1, padx=5)
        increase_button.grid(row=0, column=2, padx=5)

        # Buttons Frame
        buttons_frame = ctk.CTkFrame(self.cart_dropdown_frame, fg_color="#7C5295")
        buttons_frame.pack(pady=10)

        remove_button = ctk.CTkButton(
            buttons_frame,
            text="Remove item",
            fg_color="#52307C",
            command=self.remove_from_cart_dropdown
        )
        remove_button.pack(side="left", padx=5)

        checkout_button = ctk.CTkButton(
            buttons_frame,
            text="Checkout",
            fg_color="#52307C",
            command=self.checkout_window
        )
        checkout_button.pack(side="left", padx=5)

        total_price = self.calculate_total_price()
        self.total_label = ctk.CTkLabel(
            self.cart_dropdown_frame,
            text=f"Total: ₱{total_price:.2f}",
            font=("Arial", 14, "bold"),
            text_color="white"
        )
        self.total_label.pack(pady=5)

    def menu_dropdown(self):
        if self.dropdown_frame and self.dropdown_frame.winfo_exists():
            self.dropdown_frame.destroy()
        else:
            self.dropdown_frame = ctk.CTkFrame(self.root, fg_color="#7C5295", corner_radius=10)
            self.dropdown_frame.place(x=1230, y=60)

            ctk.CTkButton(
                self.dropdown_frame,
                text="Admin",
                width=100,
                fg_color="#7C5295",
                hover_color="#52307C",
                command=self.admin_popup
            ).pack(pady=5)

            ctk.CTkButton(
                self.dropdown_frame,
                text="Logout",
                width=100,
                fg_color="#7C5295",
                hover_color="#52307C",
                command=self.logout
            ).pack(pady=5)

            ctk.CTkButton(
                self.dropdown_frame,
                text="Exit",
                width=100,
                fg_color="#7C5295",
                hover_color="#52307C",
                command=self.exit
            ).pack(pady=5)

    def customer_section(self):
        # Title frame
        title_frame = ctk.CTkFrame(self.customer_frame, fg_color="#663a82", corner_radius=0)
        title_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            title_frame,
            text="Store Items",
            font=("Arial", 20, "bold"),
            text_color="white"
        ).pack(pady=10)

        main_frame = ctk.CTkFrame(self.customer_frame)
        main_frame.pack(fill="both", expand=True)

        # Categories frame
        categories_frame = ctk.CTkFrame(main_frame, fg_color="white", width=150)
        categories_frame.pack(side="left", fill="y")
        categories_frame.pack_propagate(False)

        # Items display frame
        items_frame = ctk.CTkFrame(main_frame, fg_color="white")
        items_frame.pack(side="right", fill="both", expand=True)

        # Group items by category
        categorized_items = {'All': []}
        for item_name, details in self.store_data.items():
            category = details.get('category', 'Uncategorized')
            categorized_items['All'].append((item_name, details))

            # Add to specific category
            if category not in categorized_items:
                categorized_items[category] = []
            categorized_items[category].append((item_name, details))

        # category buttons
        for category in categorized_items.keys():
            category_button = ctk.CTkRadioButton(
                categories_frame,
                text=category,
                text_color="black",
                variable=self.selected_category,
                value=category,
                command=lambda cat=category: self.display_items_by_category(cat, items_frame, categorized_items)
            )
            category_button.pack(pady=5, padx=10, anchor="w")

        total_price = self.calculate_total_price()

        self.total_label = ctk.CTkLabel(
            categories_frame,
            text=f"Total: ₱{total_price:.2f}",
            font=("Arial", 14, "bold"),
            text_color="black"
        )
        self.total_label.pack(side="bottom", pady=10, padx=5)

        # Initially display will be ALL
        self.display_items_by_category('All', items_frame, categorized_items)

    def display_items_by_category(self, category, items_frame, categorized_items):
            for widget in items_frame.winfo_children():
                widget.destroy()

            main_canvas = ctk.CTkCanvas(items_frame, bg="white", width=930, height=650)
            vertical_scrollbar = ctk.CTkScrollbar(items_frame, orientation="vertical", width=20,
                                                  command=main_canvas.yview)
            scrollable_frame = ctk.CTkFrame(main_canvas, fg_color="white")

            scrollable_frame.bind(
                "<Configure>",
                lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
            )
            main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            main_canvas.configure(yscrollcommand=vertical_scrollbar.set)

            main_canvas.pack(side="left", fill="both", expand=True)
            vertical_scrollbar.pack(side="right", fill="y")

            if category == "All":
                # Show items grouped by categories
                row_idx = 0
                for cat, items in categorized_items.items():
                    if cat == "All":
                        continue  # Skip the All category when displaying

                    # Add category label
                    category_label_frame = ctk.CTkFrame(scrollable_frame, fg_color="white")
                    category_label_frame.grid(row=row_idx, column=0, columnspan=8, sticky="ew", padx=15, pady=(15, 5))

                    line = ctk.CTkFrame(category_label_frame, height=3, fg_color="gray")
                    line.pack(fill="x", pady=(0, 5))

                    category_label = ctk.CTkLabel(
                        category_label_frame,
                        text=cat.upper(),
                        font=("Arial", 16, "bold"),
                        text_color="black"
                    )
                    category_label.pack(expand=True, fill="x", pady=5)
                    row_idx += 1

                    category_scroll_canvas = ctk.CTkCanvas(
                        scrollable_frame,
                        bg="white",
                        highlightthickness=0,
                        height=250,
                        width=900
                    )
                    category_scroll_canvas.grid(row=row_idx, column=0, columnspan=8, sticky="ew", padx=15, pady=5)

                    horizontal_scrollbar = ctk.CTkScrollbar(
                        scrollable_frame,
                        orientation="horizontal",
                        command=category_scroll_canvas.xview,
                        height=0
                    )
                    horizontal_scrollbar.grid(row=row_idx + 1, column=0, columnspan=8, sticky="ew", padx=15)
                    items_container = ctk.CTkFrame(category_scroll_canvas, fg_color="white")
                    category_scroll_canvas.create_window((0, 0), window=items_container, anchor="nw")

                    items_container.bind(
                        "<Configure>",
                        lambda e, canvas=category_scroll_canvas: canvas.configure(
                            scrollregion=canvas.bbox("all")
                        )
                    )
                    category_scroll_canvas.configure(xscrollcommand=horizontal_scrollbar.set)

                    def scroll_with_mouse(event):
                        main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

                    # Bind mouse scroll events
                    main_canvas.bind("<MouseWheel>", scroll_with_mouse)
                    items_frame.bind("<MouseWheel>", scroll_with_mouse)

                    # Bind mouse wheel to horizontal scrolling
                    def on_mousewheel(event, canvas=category_scroll_canvas):
                        canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

                    category_scroll_canvas.bind("<MouseWheel>", on_mousewheel)

                    # Display items for this category
                    for col_idx, (item_name, details) in enumerate(items):
                        item_frame = ctk.CTkFrame(
                            items_container,
                            fg_color="white",
                            corner_radius=10,
                            width=150,
                            height=250
                        )
                        item_frame.grid(row=0, column=col_idx, padx=10, pady=10, sticky="n")

                        img_label = ctk.CTkLabel(item_frame, text="")
                        if item_name in self.store_images and self.store_images[item_name]:
                            img_label.configure(image=self.store_images[item_name])
                            img_label.image = self.store_images[item_name]
                        img_label.pack(pady=10)

                        description = details.get("description", "No description available")
                        ctk.CTkLabel(
                            item_frame,
                            text=description,
                            font=("Arial", 12),
                            wraplength=180,
                            text_color="black",
                            anchor="center"
                        ).pack(pady=5)

                        price = details.get("price", "Price not set")
                        quantity = details.get("quantity", "0")
                        ctk.CTkLabel(
                            item_frame,
                            text=f"{price} (Qty: {quantity})",
                            font=("Arial", 12, "bold"),
                            text_color="black"
                        ).pack(pady=5)

                        select_button = ctk.CTkButton(
                            item_frame,
                            text="Add to Cart",
                            fg_color="#B491C8",
                            command=lambda item=item_name: self.add_to_cart(item)
                        )
                        select_button.pack(pady=10)

                    row_idx += 2
            else:
                # Display items for the selected category
                for col_idx, (item_name, details) in enumerate(categorized_items[category]):
                    item_frame = ctk.CTkFrame(
                        scrollable_frame,
                        fg_color="white",
                        corner_radius=10,
                        width=250,
                        height=250
                    )
                    item_frame.grid(row=0, column=col_idx, padx=10, pady=10, sticky="n")

                    img_label = ctk.CTkLabel(item_frame, text="")
                    if item_name in self.store_images and self.store_images[item_name]:
                        img_label.configure(image=self.store_images[item_name])
                        img_label.image = self.store_images[item_name]
                    img_label.pack(pady=10)

                    description = details.get("description", "No description available")
                    ctk.CTkLabel(
                        item_frame,
                        text=description,
                        font=("Arial", 12),
                        wraplength=180,
                        text_color="black",
                        anchor="center"
                    ).pack(pady=5)

                    price = details.get("price", "Price not set")
                    quantity = details.get("quantity", "0")
                    ctk.CTkLabel(
                        item_frame,
                        text=f"{price} (Qty: {quantity})",
                        font=("Arial", 12, "bold"),
                        text_color="black"
                    ).pack(pady=5)

                    select_button = ctk.CTkButton(
                        item_frame,
                        text="Add to Cart",
                        fg_color="#B491C8",
                        command=lambda item=item_name: self.add_to_cart(item)
                    )
                    select_button.pack(pady=10)

    def admin_popup(self):
        self.admin_popup = ctk.CTkToplevel(self.root)
        self.admin_popup.title("Admin Login")
        self.admin_popup.geometry("400x250")
        self.admin_popup.focus_set()
        self.admin_popup.grab_set()
        self.admin_popup.attributes("-topmost", True)
        ctk.CTkLabel(self.admin_popup, text="Admin Login", font=("Arial", 16)).pack(pady=10)

        ctk.CTkLabel(self.admin_popup, text="Username:").pack()
        self.username_entry = ctk.CTkEntry(self.admin_popup)
        self.username_entry.pack(pady=5)

        ctk.CTkLabel(self.admin_popup, text="Password:").pack()
        self.password_entry = ctk.CTkEntry(self.admin_popup, show="*")
        self.password_entry.pack(pady=5)

        login_button = ctk.CTkButton(self.admin_popup, text="Login", fg_color="#3c1361", command=self.admin_login)
        login_button.pack(pady=10)
        self.admin_popup.bind("<Return>", lambda event: login_button.invoke())

    def checkout_window(self):
        if not cart_items:
            messagebox.showinfo("Checkout", "Your cart is empty!")
            return

        if hasattr(self,
                   'cart_dropdown_frame') and self.cart_dropdown_frame and self.cart_dropdown_frame.winfo_exists():
            self.cart_dropdown_frame.destroy()

        # checkout window
        confirmation_window = ctk.CTkToplevel(self.root)
        confirmation_window.geometry("385x600")
        confirmation_window.overrideredirect(True)
        confirmation_window.attributes("-topmost", True)

        # functionality to drag the window
        def start_drag(event):
            confirmation_window.x = event.x
            confirmation_window.y = event.y

        def drag(event):
            x = confirmation_window.winfo_x() + (event.x - confirmation_window.x)
            y = confirmation_window.winfo_y() + (event.y - confirmation_window.y)
            confirmation_window.geometry(f"+{x}+{y}")

        confirmation_window.bind("<Button-1>", start_drag)
        confirmation_window.bind("<B1-Motion>", drag)

        main_frame = ctk.CTkFrame(confirmation_window, fg_color="#7C5295")
        main_frame.pack(fill="both", expand=True)

        # checkout frame
        ctk.CTkLabel(
            main_frame,
            text="Confirm Your Order",
            font=("Arial", 16, "bold"),
            text_color="black"
        ).pack(pady=10)

        # cart items frame
        cart_frame = ctk.CTkFrame(
            main_frame,
            fg_color="#F0F0F0",
            width=350,
            height=350,
        )
        cart_frame.pack(padx=10, pady=5, fill="both", expand=True)
        cart_frame.pack_propagate(False)

        canvas = tk.Canvas(cart_frame, bg="#F0F0F0", highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(cart_frame, orientation="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas, fg_color="#5e3775", width=330)

        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=330)

        for item_name, quantity in cart_items.items():
            price = float(self.store_data[item_name]['price'].replace('₱', '').replace('$', ''))
            total_price = price * quantity

            # frame for each item
            item_frame = ctk.CTkFrame(scrollable_frame, fg_color="#F0F0F0", height=80)
            item_frame.pack(fill="x", padx=5, pady=2)
            item_frame.pack_propagate(False)

            #display item image
            if 'image_path' in self.store_data[item_name]:
                try:
                    img = Image.open(self.store_data[item_name]['image_path'])
                    img = img.resize((60, 60), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)

                    image_label = tk.Label(
                        item_frame,
                        image=photo,
                        bg="#F0F0F0",
                        borderwidth=0,
                        highlightthickness=0
                    )
                    image_label.image = photo
                    image_label.pack(side="left", padx=5)
                except Exception as e:
                    print(f"Failed to load image for {item_name}: {e}")
                    empty_label = ctk.CTkLabel(item_frame, text="", width=60)
                    empty_label.pack(side="left", padx=5)

            # Item details
            details_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            details_frame.pack(side="left", fill="both", expand=True, padx=5)

            ctk.CTkLabel(
                details_frame,
                text=f"{item_name}",
                font=("Arial", 12, "bold"),
                text_color="black"
            ).pack(anchor="w")
            ctk.CTkLabel(
                details_frame,
                text=f"Qty: {quantity} | Total: ₱{total_price:.2f}",
                font=("Arial", 10),
                text_color="black"
            ).pack(anchor="w")

        scrollable_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        # Calculate the total price
        total_price = self.calculate_total_price()

        # buttons and total price
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=0)
        buttons_frame.pack(pady=10, fill="x")

        total_label = ctk.CTkLabel(
            buttons_frame,
            text=f"Total: ₱{total_price:.2f}",
            font=("Arial", 14, "bold"),
            text_color="black"
        )
        total_label.pack(side="top", pady=10)

        def cancel_checkout():
            confirmation_window.destroy()

        def confirm_checkout():
            confirmation_window.destroy()
            self.finalize_checkout()

        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            fg_color="#D9534F",
            command=cancel_checkout
        )
        cancel_button.pack(side="left", padx=10, pady=5)

        confirm_button = ctk.CTkButton(
            buttons_frame,
            text="Confirm",
            fg_color="#5CB85C",
            command=confirm_checkout
        )
        confirm_button.pack(side="right", padx=10, pady=5)

#=============================================json file methods=============================================

    def save_store_data(self):
        with open(store_data_file, 'w', encoding='utf-8') as f:
            json.dump(self.store_data, f, indent=4)

    def get_current_user_id(self):
        try:
            # Load login data from the JSON file
            with open('login.json', 'r') as f:
                login_data = json.load(f)

            # Extract the User_ID
            user_id = login_data.get('user_id')
            if not user_id:
                messagebox.showerror("Error", "No user is currently logged in.")
                return None

            return user_id
        except FileNotFoundError:
            messagebox.showerror("Error", "Login data file not found.")
            return None
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Error reading login data.")
            return None
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")
            return None

    @staticmethod
    def load_store_data():
        if Path(store_data_file).exists():
            with open(store_data_file, 'r', encoding="utf-8") as f:
                return json.load(f)
        return {}

#---------------------------------------------Methods used in cart---------------------------------------------

    def update_cart_list(self):
        if hasattr(self, 'cart_listbox'):
            self.cart_listbox.delete(0, "end")

            for item, quantity in cart_items.items():
                self.cart_listbox.insert("end", f"{item} (x{quantity})")

            self.save_store_data()

    def refresh_cart_dropdown(self):
        if hasattr(self, 'cart_dropdown_frame') and self.cart_dropdown_frame is not None:
            try:
                if self.cart_dropdown_frame.winfo_exists():
                    x = self.cart_dropdown_frame.winfo_x()
                    y = self.cart_dropdown_frame.winfo_y()

                    current_quantity = self.quantity_to_remove

                    self.cart_dropdown_frame.destroy()

                    if cart_items:
                        self.cart_dropdown()
                        self.cart_dropdown_frame.place(x=x, y=y)
                        self.quantity_to_remove = current_quantity
                        self.quantity_label.configure(text=str(self.quantity_to_remove))
            except:
                if cart_items:
                    self.cart_dropdown()

        # Update total price
        total_price = self.calculate_total_price()
        if hasattr(self, 'total_label'):
            self.total_label.configure(text=f"Total: ₱{total_price:.2f}")

    def remove_from_cart_dropdown(self):
        if self.selected_cart_item is None:
            messagebox.showinfo("Remove Item", "Please select an item to remove.")
            return

        item_name = self.selected_cart_item
        qty = cart_items[item_name]
        remove_qty = self.quantity_to_remove

        if remove_qty >= qty:
            remove_qty = qty
            cart_items.pop(item_name, None)
        else:
            cart_items[item_name] -= remove_qty

        self.store_data[item_name]["quantity"] += remove_qty
        # Update database
        self.update_database(item_name, self.store_data[item_name]["quantity"])

        self.update_cart_list()
        self.update_store_items()
        self.refresh_cart_dropdown()

    def decrease_quantity(self):
        if self.quantity_to_remove > 1:
            self.quantity_to_remove -= 1
            self.quantity_label.configure(text=str(self.quantity_to_remove))

    def increase_quantity(self):
        self.quantity_to_remove += 1
        self.quantity_label.configure(text=str(self.quantity_to_remove))
    #also used in category price total
    def calculate_total_price(self):
        total_price = sum(
            float(self.store_data.get(item, {}).get('price', '0').replace('₱', '').replace('$', '')) * qty
            for item, qty in cart_items.items()
        )
        return total_price

    def finalize_checkout(self):
        try:
            user_id = self.get_current_user_id()
            if user_id is None:
                return

            # Create a receipt and receipt items
            receipt_id = self.db_receipt(user_id)
            if receipt_id is None:
                return

            self.db_receipt_items(receipt_id, user_id)

            # Clear the cart
            cart_items.clear()

            # Update UI
            self.update_cart_list()
            self.update_store_items()

            messagebox.showinfo("Success", "Checkout completed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Error during checkout: {e}")

#--------------------------------------------------------------------------------------------------------------

# --------------------------------------Methods used for Customer Section---------------------------------------

    def horizontal_scroll(self, event, canvas):
        # Scroll horizontally based on mouse wheel position
        canvas.xview_scroll(1 if event.delta > 0 else -1, "units")

    def enable_horizontal_scroll(self, event, canvas):
        # Disable main canvas vertical scrolling
        self.main_canvas.unbind_all("<MouseWheel>")

        # Enable horizontal scrolling for this specific category canvas
        canvas.bind("<MouseWheel>", lambda e, c=canvas: self.horizontal_scroll(e, c))

    def disable_horizontal_scroll(self, event, canvas):
        # Re-enable main canvas vertical scrolling
        self.main_canvas.bind_all("<MouseWheel>",
                                  lambda event: self.main_canvas.yview_scroll(-1 * int(event.delta / 120), "units"))

        # Unbind horizontal scrolling for this category canvas
        canvas.unbind("<MouseWheel>")

    def add_to_cart(self, item_name):
        if self.store_data[item_name]["quantity"] > 0:
            self.store_data[item_name]["quantity"] -= 1
            if item_name in cart_items:
                cart_items[item_name] += 1
            else:
                cart_items[item_name] = 1
            # Update database
            self.update_database(item_name, self.store_data[item_name]["quantity"])
        else:
            messagebox.showerror("Out of Stock", f"{item_name} is out of stock!")

        self.update_cart_list()
        self.update_store_items()
        self.calculate_total_price()


        # Refresh total price if cart dropdown is open
        if hasattr(self,
                   'cart_dropdown_frame') and self.cart_dropdown_frame and self.cart_dropdown_frame.winfo_exists():
            total_price = self.calculate_total_price()
            self.total_label.configure(text=f"Total: ₱{total_price:.2f}")

    def remove_from_cart(self):
        selected_index = self.cart_listbox.curselection()
        if selected_index:
            selected_item = self.cart_listbox.get(selected_index[0])
            item_name, qty = selected_item.split(" (x")
            qty = int(qty.strip(")"))
            remove_qty = self.quantity_to_remove

            if remove_qty >= qty:
                remove_qty = qty
                cart_items.pop(item_name, None)
            else:
                cart_items[item_name] -= remove_qty

            self.store_data[item_name]["quantity"] += remove_qty
            # Update database
            self.update_database(item_name, self.store_data[item_name]["quantity"])

            self.update_cart_list()
            self.update_store_items()
            self.calculate_total_price()

        else:
            messagebox.showinfo("Remove Item", "Please select an item to remove.")

    def update_store_items(self):
        for child in self.customer_frame.winfo_children():
            child.destroy()
        self.customer_section()

    def load_store_images(self):
        for item_name, details in self.store_data.items():
            image_path = details.get("image_path")
            if image_path:
                image_path = Path(image_path).resolve()
                if image_path.exists():
                    try:
                        image = Image.open(image_path)
                        self.store_images[item_name] = CTkImage(image, size=(50, 50))
                    except Exception as e:
                        print(f"Failed to load image for {item_name}: {e}")
                else:
                    print(f"Image path does not exist for {item_name}: {image_path}")

#-------------------------------------------Methods used for menu-------------------------------------------

    def admin_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        connection = self.connect_to_database()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                # Query to check credentials
                query = """
                SELECT * FROM admin_login 
                WHERE A_Username = %s AND A_Password = %s
                """
                cursor.execute(query, (username, password))
                result = cursor.fetchone()

                if result:
                    self.admin_popup.destroy()
                    self.root.destroy()
                    subprocess.Popen([sys.executable, "admin.py"])
                else:
                    messagebox.showerror("Login Failed", "Incorrect username or password")

            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error querying database: {err}")
            finally:
                cursor.close()
                connection.close()

    def logout(self):
        # Clear the login.json file
        try:
            with open('login.json', 'w') as f:
                json.dump({}, f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not clear login data: {e}")
            return
        # Close the current application
        self.cursor.close()
        self.db_connection.close()
        self.root.destroy()

        # Open the login.py file
        subprocess.Popen([sys.executable, "login.py"])

    def exit(self):
        self.cursor.close()
        self.db_connection.close()
        self.root.destroy()
# --------------------------------------------------------------------------------------------------------------

    def run(self):
        def on_closing():
            self.save_store_data()
            self.cursor.close()
            self.db_connection.close()
            self.root.destroy()

        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        self.root.mainloop()

if __name__ == "__main__":
    root = ctk.CTk()
    app = GroceryStoreApp(root)
    app.run()