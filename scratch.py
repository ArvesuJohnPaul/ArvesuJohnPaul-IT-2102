def show_checkout_window(self):
    # Create checkout window
    checkout_window = ctk.CTkToplevel(self.root)
    checkout_window.title("Checkout")
    checkout_window.geometry("600x700")
    checkout_window.grab_set()  # Make the window modal

    # Title
    title_frame = ctk.CTkFrame(checkout_window, fg_color="#663a82", corner_radius=0)
    title_frame.pack(fill="x")
    ctk.CTkLabel(
        title_frame,
        text="Checkout",
        font=("Arial", 24, "bold"),
        text_color="white"
    ).pack(pady=15)

    # Create main frame with scrollbar
    main_frame = ctk.CTkFrame(checkout_window, fg_color="white")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Create canvas for scrolling
    canvas = tk.Canvas(main_frame, bg="white", highlightthickness=0)
    scrollbar = ctk.CTkScrollbar(main_frame, orientation="vertical", command=canvas.yview)
    scrollable_frame = ctk.CTkFrame(canvas, fg_color="white")

    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=520)

    # Headers
    headers_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
    headers_frame.pack(fill="x", padx=10, pady=(0, 10))

    ctk.CTkLabel(headers_frame, text="Item", font=("Arial", 14, "bold"), text_color="black").pack(side="left",
                                                                                                  padx=(60, 0))
    ctk.CTkLabel(headers_frame, text="Quantity", font=("Arial", 14, "bold"), text_color="black").pack(side="left",
                                                                                                      padx=(180, 0))
    ctk.CTkLabel(headers_frame, text="Price", font=("Arial", 14, "bold"), text_color="black").pack(side="right",
                                                                                                   padx=20)

    # Display cart items
    for item_name, quantity in self.cart_items.items():
        item_frame = ctk.CTkFrame(scrollable_frame, fg_color="#f5f5f5", height=80)
        item_frame.pack(fill="x", padx=10, pady=5)
        item_frame.pack_propagate(False)

        # Load and display item image
        if 'image_path' in self.store_data[item_name]:
            try:
                img = Image.open(self.store_data[item_name]['image_path'])
                img = img.resize((60, 60), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)

                image_label = tk.Label(
                    item_frame,
                    image=photo,
                    bg="#f5f5f5",
                    borderwidth=0,
                    highlightthickness=0
                )
                image_label.image = photo
                image_label.pack(side="left", padx=10)
            except Exception as e:
                print(f"Failed to load image for {item_name}: {e}")

        # Item details
        item_details = ctk.CTkFrame(item_frame, fg_color="transparent")
        item_details.pack(side="left", fill="both", expand=True, padx=10)

        ctk.CTkLabel(
            item_details,
            text=item_name,
            font=("Arial", 14),
            text_color="black"
        ).pack(side="left")

        ctk.CTkLabel(
            item_details,
            text=str(quantity),
            font=("Arial", 14),
            text_color="black"
        ).pack(side="left", padx=(180, 0))

        # Calculate and display item total price
        item_price = float(self.store_data[item_name]['price'].replace('₱', '').replace('$', ''))
        total_item_price = item_price * quantity

        ctk.CTkLabel(
            item_details,
            text=f"₱{total_item_price:.2f}",
            font=("Arial", 14),
            text_color="black"
        ).pack(side="right", padx=20)

    # Total section at the bottom
    total_frame = ctk.CTkFrame(checkout_window, height=100, fg_color="white")
    total_frame.pack(fill="x", side="bottom")
    total_frame.pack_propagate(False)

    total_price = self.calculate_total_price()

    ctk.CTkLabel(
        total_frame,
        text=f"Total Amount: ₱{total_price:.2f}",
        font=("Arial", 20, "bold"),
        text_color="black"
    ).pack(side="left", padx=20, pady=20)

    # Buttons frame
    buttons_frame = ctk.CTkFrame(total_frame, fg_color="transparent")
    buttons_frame.pack(side="right", padx=20, pady=20)

    # Cancel button
    cancel_button = ctk.CTkButton(
        buttons_frame,
        text="Cancel",
        font=("Arial", 16),
        fg_color="#ff4444",  # Red color for cancel
        width=120,
        command=lambda: self.cancel_checkout(checkout_window)
    )
    cancel_button.pack(side="left", padx=(0, 10))

    # Confirm button
    confirm_button = ctk.CTkButton(
        buttons_frame,
        text="Confirm",
        font=("Arial", 16),
        fg_color="#663a82",
        width=120,
        command=lambda: self.confirm_order(checkout_window)
    )
    confirm_button.pack(side="left")

    # Update the scroll region
    scrollable_frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))


def cancel_checkout(self, checkout_window):
    checkout_window.destroy()


def confirm_order(self, checkout_window):
    messagebox.showinfo("Success", "Order confirmed! Thank you for your purchase.")
    self.cart_items.clear()  # Clear the cart
    if self.cart_dropdown_frame and self.cart_dropdown_frame.winfo_exists():
        self.cart_dropdown_frame.destroy()  # Close cart dropdown if open
    checkout_window.destroy()  # Close checkout window

    def toggle_cart_dropdown(self):
        # Destroy existing dropdown if it exists
        if self.cart_dropdown_frame and self.cart_dropdown_frame.winfo_exists():
            self.cart_dropdown_frame.destroy()
            return

        # Create new dropdown frame
        self.cart_dropdown_frame = ctk.CTkFrame(
            self.root,
            fg_color="#7C5295",
            corner_radius=10,
            width=250,
            height=580
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

        # Create a canvas with scrollbar for cart items
        canvas_frame = ctk.CTkFrame(
            self.cart_dropdown_frame,
            fg_color="#52307C",
            width=300,
            height=360
        )
        canvas_frame.pack(padx=10, pady=5)
        # Prevent canvas frame from shrinking
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

        # Pack the scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Create a window inside the canvas for the scrollable frame
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=220)

        # Variable to track selected item
        self.selected_cart_item = None
        self.cart_items_frames = []

        def select_item(item_name, frame):
            # Deselect all frames
            for f in self.cart_items_frames:
                f.configure(fg_color="#52307C")
            # Select clicked frame
            frame.configure(fg_color="#3B2359")
            self.selected_cart_item = item_name

        # Populate cart items with images
        for item, quantity in cart_items.items():
            item_frame = ctk.CTkFrame(scrollable_frame, fg_color="#52307C", height=80)
            item_frame.pack(fill="x", padx=5, pady=2)
            item_frame.pack_propagate(False)

            # Make the entire frame clickable
            item_frame.bind("<Button-1>", lambda e, name=item, frame=item_frame: select_item(name, frame))

            # Load and resize item image
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

            # Make details frame clickable
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

        # Update the scroll region after adding all items
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

        total_price = self.calculate_total_price()
        self.total_label = ctk.CTkLabel(
            self.cart_dropdown_frame,
            text=f"Total: ₱{total_price:.2f}",
            font=("Arial", 14, "bold"),
            text_color="white"
        )

        self.total_label = ctk.CTkLabel(
            self.cart_dropdown_frame,
            text=f"Total: ₱{total_price:.2f}",
            font=("Arial", 14, "bold"),
            text_color="white"
        )
        self.total_label.pack(pady=5)

        # Add checkout button in cart dropdown
        checkout_button = ctk.CTkButton(
            self.cart_dropdown_frame,
            text="Checkout",
            font=("Arial", 12),
            fg_color="#52307C",
            command=self.show_checkout_window
        )
        checkout_button.pack(pady=(0, 10))

    def toggle_menu_dropdown(self):
        if self.dropdown_frame and self.dropdown_frame.winfo_exists():
            self.dropdown_frame.destroy()
        else:
            self.dropdown_frame = ctk.CTkFrame(self.root, fg_color="#7C5295", corner_radius=10)
            self.dropdown_frame.place(x=1230, y=60)  # Adjust position as needed

            # Add dropdown options
            ctk.CTkButton(
                self.dropdown_frame,
                text="Admin",
                width=100,
                fg_color="#7C5295",
                hover_color="#52307C",
                command=self.open_admin_popup
            ).pack(pady=5)

            ctk.CTkButton(
                self.dropdown_frame,
                text="Logout",
                width=100,
                fg_color="#7C5295",
                hover_color="#52307C",
                command=self.logout
            ).pack(pady=5)