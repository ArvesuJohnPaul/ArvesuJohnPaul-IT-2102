# ShopNGo Application README

## I. Overview

ShopNGo is a comprehensive grocery store management application designed to streamline inventory tracking, customer transactions, and user authentication. The application provides an integrated solution for both store administrators and customers, featuring a modern, user-friendly interface built with Python and CustomTkinter, and backed by a MySQL database.

## II. Features

### Login System
- Secure user authentication with hashed password storage
- User registration and login functionality
- Prevention of duplicate usernames
- Automatic login state management
- Custom, draggable login interface
- Secure SHA-256 password hashing

#### Limitations
- Stores database credentials in plain text
- Single admin/user type
- No advanced password complexity checks

### Admin Dashboard
- Comprehensive inventory management
- Add, edit, and delete product details
- Upload and display product images
- Categorize products
- Automatic database integration
- Scrollable inventory interface
- Real-time product information updates

#### Limitations
- Manual database credential configuration
- Limited product management features
- No advanced inventory analytics

### Customer Application
- Secure user authentication
- Browse products by categories
- View detailed product information
- Dynamic shopping cart functionality
- Real-time price calculations
- Checkout and transaction processing
- Automatic inventory updates
- Receipt generation

#### Limitations
- Basic product filtering
- No advanced search capabilities
- Single-location inventory management

## III. Sustainable Development Goals (SDGs)

The ShopNGo Application aligns with several UN Sustainable Development Goals:

1. **Goal 8: Decent Work and Economic Growth**
   - Supports small business digital transformation
   - Provides efficient management tools for retail operations

2. **Goal 9: Industry, Innovation, and Infrastructure**
   - Introduces technological innovation in retail management
   - Demonstrates software solutions for business process improvement

3. **Goal 12: Responsible Consumption and Production**
   - Enables accurate inventory tracking
   - Helps reduce potential waste through precise stock management

## IV. Installation and Dependencies

### System Requirements
- Python 3.8+
- MySQL Server
- Internet connection for initial setup

### Python Dependencies
Install the following packages using pip:

```bash
pip install customtkinter pillow mysql-connector-python
