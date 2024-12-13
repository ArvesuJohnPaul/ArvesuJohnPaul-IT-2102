import json
from pathlib import Path
from PIL import Image, ImageTk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import shutil
import os
import mysql.connector

image_folder_path = r'C:\Users\arves\Documents\CODES\Final_proj_ShopNGo\img_item'
image_file_extensions = {'.jpg', '.png'}
store_data_file = 'store_data.json'

# add here for categories
categories = [
    "canned food", "frozen", "fresh", "beverage", "bread",
    "chips", "dairy", "snacks", "condiments"
]


def connect_to_database():
    try:
        initial_conn = mysql.connector.connect(
            host="localhost",
            user="POPE",
            password="april435"
        )
        initial_cursor = initial_conn.cursor()

        # Create database if it doesn't exist
        initial_cursor.execute("CREATE DATABASE IF NOT EXISTS store_data")
        initial_cursor.close()
        initial_conn.close()

        # Now connect to the specific database
        conn = mysql.connector.connect(
            host="localhost",
            user="POPE",
            password="april435",
            database="store_data"
        )
        cursor = conn.cursor()

        # Create item_data table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS item_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            item_name VARCHAR(255) UNIQUE NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            quantity INT NOT NULL,
            category VARCHAR(100) NOT NULL
        )
        """)
        conn.commit()

        return conn, cursor

    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Could not connect to or create database: {e}")
        return None, None


class App:
    def __init__(self, image_folder_path, image_file_extensions):
        # Database connection
        self.db, self.cursor = connect_to_database()
        if not self.db:
            messagebox.showerror("Database Error", "Failed to connect to database. Exiting.")
            return

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Admin")
        self.image_folder_path = Path(image_folder_path)
        self.image_file_extensions = image_file_extensions
        self.store_data = self.load_descriptions()
        self.create_widgets()
        self.list_images()
        self.show_images()

        # Handle's the app close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.root.mainloop()

    def on_close(self):
        if hasattr(self, 'db') and self.db.is_connected():
            self.db.close()
        self.root.destroy()
        os.system('python main.py')

    def create_widgets(self):
        # Header
        self.header_label = ctk.CTkLabel(self.root, text="Admin", font=("Arial", 24, "bold"))
        self.header_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Add Item Button
        self.add_item_btn = ctk.CTkButton(self.root, text='Add Item', fg_color="#3c1361",
                                          command=self.open_add_item_popup)
        self.add_item_btn.grid(row=1, column=0, columnspan=2, pady=10)

        self.text = ScrolledText(self.root, wrap="word", width=50, height=20)
        self.text.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    def open_add_item_popup(self):
        popup = ctk.CTkToplevel(self.root)
        popup.title("Add Item")
        popup.geometry("500x600")
        popup.transient(self.root)
        popup.grab_set()
        # Header
        popup_header = ctk.CTkLabel(popup, text="Add Item", font=("Arial", 20, "bold"))
        popup_header.grid(row=0, column=0, columnspan=2, pady=10)

        # input new file name
        filename_label = ctk.CTkLabel(popup, text="Enter Item Name:")
        filename_label.grid(row=1, column=0, padx=10, pady=5)

        filename_entry = ctk.CTkEntry(popup, width=300)
        filename_entry.grid(row=1, column=1, padx=10, pady=5)

        # input image description
        description_label = ctk.CTkLabel(popup, text="Enter Description:")
        description_label.grid(row=2, column=0, padx=10, pady=5)

        description_entry = ctk.CTkEntry(popup, width=300)
        description_entry.grid(row=2, column=1, padx=10, pady=5)

        # input price
        price_label = ctk.CTkLabel(popup, text="Enter Price:")
        price_label.grid(row=3, column=0, padx=10, pady=5)

        price_entry = ctk.CTkEntry(popup, width=300)
        price_entry.grid(row=3, column=1, padx=10, pady=5)

        # input Quantity
        quantity_label = ctk.CTkLabel(popup, text="Enter Quantity:")
        quantity_label.grid(row=4, column=0, padx=10, pady=5)

        quantity_entry = ctk.CTkEntry(popup, width=300)
        quantity_entry.grid(row=4, column=1, padx=10, pady=5)

        # select category
        category_label = ctk.CTkLabel(popup, text="Select Category:")
        category_label.grid(row=5, column=0, padx=10, pady=5)

        category_var = ctk.StringVar(value=categories[0])
        category_dropdown = ctk.CTkOptionMenu(popup, fg_color="#3c1361", values=categories, variable=category_var)
        category_dropdown.grid(row=5, column=1, padx=10, pady=5)

        # upload image
        upload_btn = ctk.CTkButton(
            popup,
            text="Upload Image",
            fg_color="#3c1361",
            command=lambda: self.upload_image(popup, filename_entry, description_entry, price_entry, quantity_entry,
                                              category_var, image_label)
        )
        upload_btn.grid(row=6, column=0, columnspan=2, pady=10)

        # Placeholder for uploaded image display
        image_label = ctk.CTkLabel(popup, text="No image uploaded", width=200, height=100, anchor="center")
        image_label.grid(row=7, column=0, columnspan=2, pady=10)

        # save item
        save_btn = ctk.CTkButton(
            popup,
            text="Save Item",
            fg_color="#3c1361",
            command=lambda: self.save_item(popup, filename_entry, description_entry, price_entry, quantity_entry,
                                           category_var)
        )
        save_btn.grid(row=8, column=0, columnspan=2, pady=10)

    def upload_image(self, popup, filename_entry, description_entry, price_entry, quantity_entry, category_var,
                     image_label):
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image Files", "*.png")]
        )

        if file_path:
            try:
                img = Image.open(file_path).resize((200, 200))
                img_tk = ImageTk.PhotoImage(img)

                image_label.configure(image=img_tk, text="")  # Remove placeholder text
                image_label.image = img_tk

                popup.temp_image_path = file_path
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")

    def save_item(self, popup, filename_entry, description_entry, price_entry, quantity_entry, category_var):
        file_path = getattr(popup, 'temp_image_path', None)
        if not file_path:
            messagebox.showerror("Error", "No image uploaded.")
            return

        new_filename = filename_entry.get().strip()
        if not new_filename:
            messagebox.showerror("Filename Error", "Please enter a filename.")
            return

        new_filename = Path(new_filename).with_suffix(Path(file_path).suffix).name
        destination = self.image_folder_path / new_filename
        if destination.exists():
            response = messagebox.askyesno("File Exists", "Do you want to overwrite it?")
            if not response:
                return

        try:
            quantity = int(quantity_entry.get())
            price = float(price_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity or price. Please enter numbers.")
            return

        description = description_entry.get()
        category = category_var.get()

        try:
            shutil.copy(file_path, destination)

            self.store_data[new_filename.rsplit('.', 1)[0]] = {
                "description": description,
                "price": f"₱{price:.2f}",
                "quantity": quantity,
                "category": category,
                "image_path": str(destination)
            }

            # Save to database
            self.cursor.execute(
                "INSERT INTO item_data (item_name, price, quantity, category) VALUES (%s, %s, %s, %s)",
                (new_filename.rsplit('.', 1)[0], price, quantity, category)
            )
            self.db.commit()
            self.save_store_data()
            self.list_images()
            self.show_images()
            popup.destroy()

            messagebox.showinfo("Success", "Item saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def edit_item(self, image_file_path):
        filename_without_extension = image_file_path.stem
        item_data = self.store_data.get(filename_without_extension, {})

        popup = ctk.CTkToplevel(self.root)
        popup.title("Edit Item")
        popup.geometry("500x600")
        popup.transient(self.root)  # Keep popup above the main window
        popup.grab_set()  # Focus on this popup

        # Header
        popup_header = ctk.CTkLabel(popup, text="Edit Item", font=("Arial", 20, "bold"))
        popup_header.grid(row=1, column=0, columnspan=2, pady=10)

        # edit item name
        filename_label = ctk.CTkLabel(popup, text="Item Name:")
        filename_label.grid(row=2, column=0, padx=10, pady=5)
        filename_entry = ctk.CTkEntry(popup, width=300)
        filename_entry.insert(0, filename_without_extension)
        filename_entry.grid(row=2, column=1, padx=10, pady=5)

        # edit description
        description_label = ctk.CTkLabel(popup, text="Description:")
        description_label.grid(row=3, column=0, padx=10, pady=5)
        description_entry = ctk.CTkEntry(popup, width=300)
        description_entry.insert(0, item_data.get("description", ""))
        description_entry.grid(row=3, column=1, padx=10, pady=5)

        # edit price
        price_label = ctk.CTkLabel(popup, text="Price:")
        price_label.grid(row=4, column=0, padx=10, pady=5)
        price_entry = ctk.CTkEntry(popup, width=300)
        price_entry.insert(0, item_data.get("price", "").replace("₱", ""))
        price_entry.grid(row=4, column=1, padx=10, pady=5)

        # edit quantity
        quantity_label = ctk.CTkLabel(popup, text="Quantity:")
        quantity_label.grid(row=5, column=0, padx=10, pady=5)
        quantity_entry = ctk.CTkEntry(popup, width=300)
        quantity_entry.insert(0, str(item_data.get("quantity", "")))
        quantity_entry.grid(row=5, column=1, padx=10, pady=5)

        # category
        category_label = ctk.CTkLabel(popup, text="Category:")
        category_label.grid(row=6, column=0, padx=10, pady=5)
        category_var = ctk.StringVar(value=item_data.get("category", categories[0]))
        category_dropdown = ctk.CTkOptionMenu(popup, values=categories, variable=category_var)
        category_dropdown.grid(row=6, column=1, padx=10, pady=5)

        # upload a new image
        upload_btn = ctk.CTkButton(
            popup,
            text="Upload New Image",
            fg_color="#3c1361",
            command=lambda: self.upload_new_image(image_label, popup)
        )
        upload_btn.grid(row=7, column=0, columnspan=2, pady=10)

        # display current item as placeholder
        current_img = Image.open(image_file_path).resize((200, 200), Image.Resampling.LANCZOS)
        current_img_tk = ImageTk.PhotoImage(current_img)
        image_label = ctk.CTkLabel(popup, image=current_img_tk, text="")
        image_label.image = current_img_tk  # Keep reference to avoid garbage collection
        image_label.grid(row=8, column=0, columnspan=2, pady=10)

        # Save
        save_btn = ctk.CTkButton(
            popup,
            text="Save Changes",
            fg_color="#3c1361",
            command=lambda: self.save_edited_item(
                popup,
                image_file_path,
                filename_entry,
                description_entry,
                price_entry,
                quantity_entry,
                category_var
            )
        )
        save_btn.grid(row=9, column=0, columnspan=2, pady=10)

    def upload_new_image(self, image_label, popup):
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
        )

        if file_path:
            try:
                new_img = Image.open(file_path).resize((200, 200), Image.Resampling.LANCZOS)
                new_img_tk = ImageTk.PhotoImage(new_img)

                image_label.configure(image=new_img_tk, text="")
                image_label.image = new_img_tk

                popup.temp_image_path = file_path
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")

    def save_edited_item(self, popup, image_file_path, filename_entry, description_entry, price_entry, quantity_entry,
                         category_var):
        try:
            new_filename = filename_entry.get().strip()
            description = description_entry.get().strip()
            price = float(price_entry.get())
            quantity = int(quantity_entry.get())
            category = category_var.get()
            file_path = getattr(popup, 'temp_image_path', None)

            new_image_path = self.image_folder_path / f"{new_filename}{image_file_path.suffix}"
            if new_filename != image_file_path.stem:
                os.rename(image_file_path, new_image_path)
                del self.store_data[image_file_path.stem]
            else:
                new_image_path = image_file_path

            if file_path:
                shutil.copy(file_path, new_image_path)

            # Update json
            self.store_data[new_filename] = {
                "description": description,
                "price": f"₱{price:.2f}",
                "quantity": quantity,
                "category": category,
                "image_path": str(new_image_path)
            }

            # Update database
            self.cursor.execute(
                "UPDATE item_data SET item_name=%s, price=%s, quantity=%s, category=%s WHERE item_name=%s",
                (new_filename, price, quantity, category, image_file_path.stem)
            )
            self.db.commit()
            self.save_store_data()
            self.list_images()
            self.show_images()
            popup.destroy()
            messagebox.showinfo("Success", "Item updated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {e}")

    def list_images(self):
        self.image_files = [filepath for filepath in self.image_folder_path.iterdir() if
                            filepath.suffix in self.image_file_extensions]

    def show_images(self):
        if hasattr(self, 'scroll_frame'):
            self.scroll_frame.destroy()

        self.scroll_frame = ctk.CTkScrollableFrame(self.root, width=1000, height=600)
        self.scroll_frame.grid(row=2, column=0, columnspan=9, padx=10, pady=10)

        for col in range(9):
            self.scroll_frame.columnconfigure(col, weight=1, uniform="uniform_col")

        header_labels = [
            ("Item Image", 0, 1),
            ("Item Name", 1, 1),
            ("Description", 2, 3),
            ("Price", 5, 1),
            ("Quantity", 6, 1),
            ("Category", 7, 1),
            ("Actions", 8, 1),
        ]
        for text, col, span in header_labels:
            label = ctk.CTkLabel(self.scroll_frame, text=text, font=("Arial", 14, "bold"))
            label.grid(row=0, column=col, columnspan=span, padx=5, pady=5, sticky="w")

        for col in range(9):
            divider = ctk.CTkLabel(self.scroll_frame, text="", height=2, fg_color="black")
            divider.grid(row=1, column=col, padx=1, pady=1, sticky="ew")

        # action button images
        edit_image = ImageTk.PhotoImage(Image.open("img/edit.png").resize((32, 32), Image.Resampling.LANCZOS))
        delete_image = ImageTk.PhotoImage(Image.open("img/delete.png").resize((32, 32), Image.Resampling.LANCZOS))

        # inserts datas into item_data
        for i, image_file_path in enumerate(self.image_files, start=2):
            img = Image.open(image_file_path).resize((64, 64), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)

            # get item details
            filename_without_extension = image_file_path.stem
            item_data = self.store_data.get(filename_without_extension, {})
            description = item_data.get("description", "No description available")
            price = item_data.get("price", "Price not set")
            category = item_data.get("category", "No category")
            quantity = item_data.get("quantity", "Quantity not set")

            # item image (Column 0)
            image_label = ctk.CTkLabel(self.scroll_frame, image=img_tk, text="")
            image_label.image = img_tk  # Keep reference to avoid garbage collection
            image_label.grid(row=i, column=0, padx=5, pady=5)

            # item name (Column 1)
            name_label = ctk.CTkLabel(self.scroll_frame, text=filename_without_extension, font=("Arial", 12))
            name_label.grid(row=i, column=1, padx=5, pady=5, sticky="w")

            # description (Columns 2-4)
            description_label = ctk.CTkLabel(
                self.scroll_frame,
                text=description,
                wraplength=500,  # Ensure text spans properly
                font=("Arial", 10),
            )
            description_label.grid(row=i, column=2, columnspan=3, padx=5, pady=5, sticky="w")

            # price (Column 5)
            price_label = ctk.CTkLabel(self.scroll_frame, text=price, font=("Arial", 12))
            price_label.grid(row=i, column=5, padx=5, pady=5, sticky="w")

            # quantity (Column 6)
            quantity_label = ctk.CTkLabel(self.scroll_frame, text=str(quantity), font=("Arial", 12))
            quantity_label.grid(row=i, column=6, padx=5, pady=5, sticky="w")

            # category (Column 7)
            category_label = ctk.CTkLabel(self.scroll_frame, text=category, font=("Arial", 12))
            category_label.grid(row=i, column=7, padx=5, pady=5, sticky="w")

            # actions (Column 8)
            action_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            action_frame.grid(row=i, column=8, padx=5, pady=5, sticky="ew")

            # edit Button
            edit_button = ctk.CTkButton(
                action_frame, text="", image=edit_image, width=20, fg_color="#3c1361", height=20,
                command=lambda img=image_file_path: self.edit_item(img)
            )
            edit_button.pack(side="left")

            # delete Button
            delete_button = ctk.CTkButton(
                action_frame, text="", image=delete_image, width=32, fg_color="#3c1361", height=32,
                command=lambda img=image_file_path: self.remove_image(img)
            )
            delete_button.pack(side="left", padx=5)

    def remove_image(self, image_file_path):
        response = messagebox.askyesno(
            "Delete Image",
            f"Are you sure you want to delete {image_file_path.name}?"
        )
        if response:
            try:
                # remove the image file
                image_file_path.unlink()

                # Remove metadata from descriptions
                item_name = image_file_path.stem
                if item_name in self.store_data:
                    del self.store_data[item_name]

                self.save_store_data()
                self.list_images()
                self.show_images()

                messagebox.showinfo("Image Removed", f"{image_file_path.name} has been removed.")
            except Exception as e:
                messagebox.showerror("Remove Failed", f"Failed to remove image: {e}")

    def save_store_data(self):
        with open(store_data_file, 'w') as f:
            json.dump(self.store_data, f, indent=4)
        print(f"Store data saved to {store_data_file}")

    def load_descriptions(self):
        if Path(store_data_file).exists():
            with open(store_data_file, 'r') as f:
                return json.load(f)
        return {}


App(image_folder_path, image_file_extensions)