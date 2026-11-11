# 🔥 PETROL BUDDY — Online Petrol Delivery System
### College Mini-Project | Python (Flask) + MySQL + HTML5 + CSS3 + Vanilla JavaScript

---

## 📌 Project Overview
**Petrol Buddy** is a responsive full-stack online fuel delivery web application developed with **Python (Flask)** and **MySQL**. It replicates an on-demand fuel procurement service that allows customers to request doorstep petrol and diesel delivery, coordinates dispatch through delivery Bowser operators, and offers administrators comprehensive inventory and sales controls.

- **Frontend:** HTML5, CSS3 (Custom Responsive Design System), JavaScript (ES6)
- **Backend:** Python 3 (Flask framework, Werkzeug security, Blueprints)
- **Database:** MySQL / MariaDB (via `mysql-connector-python`)
- **Architecture:** Role-Based Access Control (Admin, Customer, Delivery Partner)

---

## 📁 Project Folder Structure

```
pardhu project/
│
├── app.py                      # Flask Application Factory & Entry Point
├── auth_helpers.py             # Route Security Decorators (@login_required, @role_required)
├── db.py                       # MySQL Query Helper & Atomic Transactions
├── setup_db.py                 # Automated Database Initializer & Password Hasher
├── petrol_buddy.sql            # MySQL Database Schema + Seed Data
├── requirements.txt            # Python Dependencies
├── .env                        # Database & Secret Key Configuration
│
├── routes/                     # Modular Flask Blueprints
│   ├── __init__.py
│   ├── public.py               # Home, About, Contact
│   ├── auth.py                 # Unified Login, Customer Registration, Logout
│   ├── customer.py             # Dashboard, Place Order, Tracking, Feedback, Profile
│   ├── admin.py                # Dashboard, Orders, Stock, Pricing, Partners, Reports
│   └── delivery.py             # Dashboard, Assigned Orders, Delivery Details, History
│
├── static/                     # Static Assets (Offline-Ready)
│   ├── css/
│   │   └── style.css           # Navy/Orange Design System, Cards, Badges, Print Styles
│   └── js/
│       └── script.js           # Live Price Calc, Browser GPS, Rating Picker, Demo Fillers
│
└── templates/                  # Jinja2 HTML Templates
    ├── base.html               # Master Layout (Navbar, Sidebar, Footer, Flash)
    ├── index.html              # Landing Page with Live Prices & Features
    ├── about.html              # About & Academic Information
    ├── contact.html            # Contact Form & Emergency Hotlines & FAQ
    ├── login.html              # Unified Login with 1-Click Demo Buttons
    ├── register.html           # Customer Registration
    ├── 404.html                # Not Found Error Page
    ├── 403.html                # Access Denied Error Page
    │
    ├── customer/
    │   ├── dashboard.html      # KPI Cards & Recent Orders
    │   ├── place_order.html    # Order Fuel Form (Live Price + Browser GPS)
    │   ├── my_orders.html      # Tabulated Orders List + Cancellation
    │   ├── track_order.html    # 5-Stage Live Status Visual Timeline
    │   ├── feedback.html       # Interactive 5-Star Rating & Review
    │   └── profile.html        # Profile Update & Password Change
    │
    ├── admin/
    │   ├── dashboard.html      # Admin KPI Cards, Low Stock Warning & Activity
    │   ├── manage_orders.html  # Order Workflow (Confirm, Reject, Assign, Cancel)
    │   ├── manage_inventory.html# Fuel Stock Add / Calibrate / Thresholds
    │   ├── manage_prices.html  # Set Unit Petrol & Diesel Rates per Litre
    │   ├── manage_customers.html# View & Activate/Deactivate Accounts
    │   ├── manage_delivery_partners.html # Fleet Management & Bowser Reg
    │   ├── manage_payments.html# COD & Simulated Digital Transactions
    │   ├── manage_feedback.html# Moderation of Customer Ratings
    │   └── reports.html        # Sales Analytics & Printable Summaries
    │
    └── delivery/
        ├── dashboard.html      # Pilot Dashboard & Assigned Deliveries
        ├── assigned_orders.html# Queued Order Dispatch List
        ├── order_details.html  # GPS Navigation, Fuel Dispensing & Status Actions
        ├── delivery_history.html# Historical Completed Services
        └── profile.html        # Duty Availability Toggle & Vehicle Reg
```

---

## 🚀 Quick Setup Instructions

### Prerequisites
1. **Python 3.8+** installed on your system.
2. **MySQL Server** running (via XAMPP, MySQL Installer, or Docker).

### Step 1: Clone or Navigate to the Folder
Open PowerShell / Terminal and navigate to the project directory:
```bash
cd "C:\Users\LENOVO\Desktop\pardhu project"
```

### Step 2: Create and Activate Virtual Environment (Recommended)
```bash
# Create venv
python -m venv venv

# Activate venv on Windows:
.\venv\Scripts\activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Database Connection
Open `.env` and verify your MySQL settings (XAMPP default has empty password):
```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=petrol_buddy
SECRET_KEY=petrolbuddy_super_secret_key_2026
```

### Step 5: Initialize MySQL Database
Make sure MySQL is running, then execute the automated initializer:
```bash
python setup_db.py
```
*This automatically builds all 9 tables, inserts sample records, and encrypts passwords with Werkzeug.*

### Step 6: Start the Flask Application
```bash
python app.py
```

Open your browser and navigate to:
👉 **http://127.0.0.1:5000**

---

## 🔑 Demo Login Credentials

You can test all three roles immediately using the built-in demo credentials (or click the **Quick Demo** buttons on the login page):

| Role | Email | Password | Panel |
|------|-------|----------|-------|
| 🛡️ **Administrator** | `admin@petrolbuddy.com` | `Admin@123` | `/admin/dashboard` |
| 👤 **Customer** | `customer@petrolbuddy.com` | `Customer@123` | `/customer/dashboard` |
| 🚚 **Delivery Partner** | `delivery@petrolbuddy.com` | `Delivery@123` | `/delivery/dashboard` |

---

## 🧪 Key Functionalities Included

### 👤 Customer Module
- **Registration & Login:** Validation, duplicate email prevention, password encryption with Werkzeug `generate_password_hash`.
- **Order Placement:** Live JavaScript order price calculator, browser HTML5 Geolocation (`navigator.geolocation`) without external map APIs, live stock checking.
- **Order Tracking:** 5-step visual timeline:
  `Placed` &rarr; `Confirmed` &rarr; `Partner Assigned` &rarr; `Out for Delivery` &rarr; `Delivered`.
- **Order Cancellation:** Customers can cancel orders before dispatch, which automatically restores fuel inventory.
- **Feedback:** Star-rating picker for delivered orders with review message.

### 🛡️ Admin Module
- **Dashboard:** Real-time KPI summary (total orders, today's orders, revenue, fuel stock warnings).
- **Order Management:** Filter by status/date/search, confirm orders, reject with reason, assign available partners.
- **Inventory & Pricing:** Live stock calibration, low-stock threshold alerts, live rate updates per litre.
- **Partner Fleet:** Register new delivery pilots with vehicle numbers, toggle availability, activate/deactivate accounts.
- **Reports:** Printable sales summary with date and fuel-type filtering.

### 🚚 Delivery Partner Module
- **Duty Availability:** Toggle on-duty/off-duty status to receive or pause assignments.
- **Assigned Deliveries:** View customer address, landmarks, contact numbers, and optional coordinates.
- **Status Updates:** Advance status from `Partner Assigned` &rarr; `Out for Delivery` &rarr; `Delivered`.
- **COD Collection:** Confirms cash payment receipt upon fuel dispensing.

---

*Designed & Developed by **Pardhu** | College Mini-Project Demonstration*
