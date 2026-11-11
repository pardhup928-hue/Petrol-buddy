# PETROL BUDDY – ONLINE PETROL DELIVERY SYSTEM
## Complete College Mini-Project Technical Documentation

---

## 1. Project Abstract
**Petrol Buddy** is a responsive, full-stack web-based online petrol delivery management system built with **Python (Flask)**, **MySQL**, and modern frontend technologies (**HTML5, CSS3, JavaScript**). The application addresses the traditional bottlenecks of automotive and generator refueling by facilitating doorstep fuel delivery. The system establishes a structured three-tier architecture providing tailored dashboards for **Customers**, **Administrators**, and **Delivery Partners**. Customers can register, schedule petrol or diesel orders, capture delivery coordinates using browser geolocation, track progress through an interactive 5-stage timeline, and submit service ratings. Administrators control daily fuel rates, manage stock inventory with transactional safety, and assign orders to mobile Bowser operators. Delivery pilots navigate to customer destinations and update status transitions in real time. The entire application operates 100% locally on Python and MySQL without requiring external paid APIs.

---

## 2. Introduction
Automotive mobility and industrial backup power rely heavily on consistent petroleum access. However, traditional procurement requires physical travel to stationary petrol stations, often leading to wasted time in traffic queues, fuel exhaustion on isolated highways, and logistical overhead for commercial generators and corporate vehicle fleets.

**Petrol Buddy** digitizes this supply chain by introducing an on-demand fuel distribution portal. Inspired by modern quick-commerce and PESO-compliant mobile refueling initiatives, the software connects consumers with mobile fuel Bowser operators under strict administrative supervision.

---

## 3. Problem Statement
The conventional fuel procurement model exhibits key pain points:
1. **Physical Commute Overhead:** Vehicle owners must divert from their routes to visit fuel stations, contributing to urban congestion and idling emissions.
2. **Roadside Emergencies:** Stranded motorists on highways or outskirts have no standardized on-demand fuel delivery assistance.
3. **Generator Inconvenience:** Commercial and residential standby generators require transport of hazardous loose fuel in uncertified containers (cans/barrels), posing extreme safety hazards.
4. **Lack of Centralized Tracking:** Fleet managers and bulk consumers lack a unified digital audit trail for fuel expenditure, delivery verification, and consumption analytics.

---

## 4. Existing System
In the existing ecosystem, fuel acquisition is entirely location-bound:
- Consumers travel to fixed physical retail outlets.
- Manual queueing and physical cash/POS payments dominate transactions.
- Emergency roadside refueling depends on ad-hoc assistance or towing services.
- Stock and accounting reconciliation at pump stations are often maintained via disparate legacy POS terminals.

**Disadvantages of Existing System:**
- Inflexible and time-consuming.
- High risk of fire hazards during manual fuel transportation in portable containers.
- Absence of real-time delivery status updates.
- No direct mechanism to link fuel dispenser flow-meters with customer order receipts.

---

## 5. Proposed System
**Petrol Buddy** provides an end-to-end web-based platform with three dedicated access portals:
- **Customer Portal:** Easy registration, fuel selection (Petrol/Diesel), automatic cost calculation, browser-based location sharing, 5-stage delivery tracking, and feedback logging.
- **Admin Management Portal:** Dynamic daily pricing controls, stock deduction with database transactions, delivery partner onboarding, order dispatching, and printable analytics.
- **Delivery Partner Portal:** Active job queue, customer address/coordinate inspection, status transitions (`Partner Assigned` &rarr; `Out for Delivery` &rarr; `Delivered`), and COD payment collection.

**Advantages of Proposed System:**
- Complete doorstep convenience 24/7.
- Zero external API dependencies (works completely offline and locally).
- Secure role-based authorization using Flask session management and Werkzeug password hashing.
- Inventory safety: atomic database transactions ensure stock consistency and prevent overselling.

---

## 6. Objectives
1. Design an intuitive, responsive user interface supporting mobile and desktop viewports.
2. Implement secure authentication with Werkzeug password encryption (`pbkdf2:sha256`) and role separation.
3. Automate live pricing and order total calculations using client-side JavaScript validated on the server.
4. Provide browser-based geolocation capture without requiring Google Maps API keys.
5. Create an interactive 5-stage visual delivery tracker.
6. Enable atomic stock deduction and automated inventory rollback on order cancellation/rejection.
7. Generate printable sales reports and fuel consumption analytics for administrative review.

---

## 7. Hardware Requirements
| Hardware Component | Minimum Specification | Recommended Specification |
|---|---|---|
| Processor | Dual-Core Intel Core i3 / AMD Ryzen 3 | Quad-Core Intel Core i5 / AMD Ryzen 5 |
| RAM | 4 GB | 8 GB or higher |
| Storage | 1 GB available disk space | SSD with 5 GB free space |
| Network | Localhost connection (No active internet required) | Localhost connection |
| Screen Resolution | 1024 × 768 | 1920 × 1080 (Full HD) |

---

## 8. Software Requirements
| Software | Component | Purpose |
|---|---|---|
| Operating System | Windows 10/11, Linux, or macOS | Host Operating Environment |
| Programming Language | Python 3.8 to 3.12 | Backend Application Engine |
| Web Framework | Flask 3.0+ | Microframework, Routing & Blueprints |
| Template Engine | Jinja2 | Dynamic HTML Rendering & Filters |
| Security | Werkzeug | Password Hashing (`generate_password_hash`) |
| Database | MySQL 5.7+ / MariaDB 10.3+ | Relational Database Management System |
| Database Driver | `mysql-connector-python` | Python-to-MySQL Database Connector |
| Web Browser | Google Chrome, Mozilla Firefox, Edge | Client Interface Execution |

---

## 9. Functional Requirements

### A. Customer Module
- **Self-Registration:** Customer accounts capture full name, email, phone, street address, city, and pincode with email uniqueness checks.
- **Authentication:** Session-based authentication with role verification and logout.
- **Fuel Booking:** Select fuel type (Petrol/Diesel), input volume (5L to 100L), automatic price calculation, delivery date/time picker, payment mode selection.
- **Location Pinning:** Manual address entry supplemented with 1-click HTML5 GPS coordinate capture (`navigator.geolocation`).
- **Live Order Tracking:** 5-step status progression timeline.
- **Cancellation:** Customers may cancel orders while in `Placed` or `Confirmed` state, triggering automatic stock restoration.
- **Feedback:** Star-rating submission (1–5 stars) with comments for completed orders.
- **Profile:** Manage contact coordinates and update login password.

### B. Admin Module
- **Dashboard Metrics:** Summary cards showing total orders, today's orders, revenue, active deliveries, and low-stock alerts.
- **Order Management:** View, search, and filter orders by date or status; confirm or reject orders (with rejection reason); assign available delivery partners.
- **Inventory Control:** View stock reserves, add stock, recalibrate quantity, and configure low-stock safety thresholds.
- **Pricing Control:** Update daily unit price per litre for Petrol and Diesel.
- **Partner Management:** Onboard mobile Bowser operators with vehicle registration numbers; activate or deactivate accounts; toggle duty status.
- **Payment Auditing:** Review COD receipts and simulated digital payments.
- **Reporting & Export:** Generate filtered sales reports with a print-ready layout (`@media print`).

### C. Delivery Partner Module
- **Pilot Dashboard:** View assigned order count, ongoing jobs, and completed deliveries.
- **Assigned Deliveries:** Detailed view of customer destination, landmark, phone contact, and fuel volume.
- **Fulfillment Workflow:** Update order state from `Partner Assigned` &rarr; `Out for Delivery` &rarr; `Delivered`.
- **Payment Collection:** Collect and record Cash on Delivery payments upon fuel delivery.
- **Duty Availability:** Toggle online/offline status.

---

## 10. Non-Functional Requirements
- **Security:** Zero plaintext password storage (all passwords hashed via Werkzeug); SQL injection prevention through parameterized queries; session isolation between roles.
- **Performance:** Sub-100ms local server response times; efficient indexed MySQL queries.
- **Usability:** High contrast navy/orange fuel theme; clear badge indicators; responsive hamburger menu for mobile devices.
- **Reliability:** Atomic database transactions ensure order generation and inventory deduction succeed or fail together.
- **Maintainability:** Modular Flask Blueprints (`routes/public.py`, `routes/auth.py`, `routes/customer.py`, `routes/admin.py`, `routes/delivery.py`).

---

## 11. System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                       CLIENT BROWSER                        │
│         HTML5 / CSS3 (Navy & Fuel Orange) / Vanilla JS      │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / HTTPS (RESTful Requests)
┌──────────────────────────────▼──────────────────────────────┐
│                    FLASK APPLICATION SERVER                 │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                 app.py (Factory)                    │   │
│   │   auth_helpers.py (@login_required, @role_required) │   │
│   │   db.py (Query Helper & Transaction Handler)        │   │
│   └──────────────────────────┬──────────────────────────┘   │
│                              │                              │
│      ┌───────────────────────┼───────────────────────┐      │
│      │                       │                       │      │
│ ┌────▼────────┐      ┌───────▼──────┐       ┌────────▼────┐ │
│ │  Customer   │      │    Admin     │       │  Delivery   │ │
│ │  Blueprint  │      │  Blueprint   │       │  Blueprint  │ │
│ └─────────────┘      └──────────────┘       └─────────────┘ │
└──────────────────────────────┬──────────────────────────────┘
                               │ Parameterized SQL Queries
┌──────────────────────────────▼──────────────────────────────┐
│                  MySQL DATABASE SERVER                      │
│                                                             │
│  Database: petrol_buddy                                     │
│  Tables: users, customers, admins, delivery_partners,       │
│          fuel_inventory, fuel_prices, orders, payments,     │
│          feedback                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 12. Data Flow Diagram (DFD)

### Level 0 — Context Level DFD
```
                 Customer Credentials & Orders
  [CUSTOMER] ────────────────────────────────────► ┌───────────────┐
             ◄──────────────────────────────────── │               │
                 Order Confirmation & Tracking     │               │
                                                   │ PETROL BUDDY  │
                 Price Updates & Partner Dispatch  │    SYSTEM     │
  [ADMIN]    ────────────────────────────────────► │               │
             ◄──────────────────────────────────── │  (Python &    │
                 Sales Reports & Analytics         │    MySQL)     │
                                                   │               │
                 Duty Status & Delivery Completion │               │
  [DELIVERY] ────────────────────────────────────► │               │
  [PARTNER]  ◄──────────────────────────────────── └───────────────┘
                 Assigned Order Details
```

### Level 1 DFD
```
Customer ──► [1.0 Registration & Login] ──► (users, customers)
Customer ──► [2.0 Place Fuel Order]     ──► (orders, fuel_inventory, payments)
Customer ──► [3.0 Track Order]          ◄── (orders, delivery_partners)
Customer ──► [4.0 Submit Feedback]      ──► (feedback)

Admin    ──► [5.0 Manage Inventory]     ──► (fuel_inventory)
Admin    ──► [6.0 Update Fuel Pricing]  ──► (fuel_prices)
Admin    ──► [7.0 Assign Partner]       ──► (orders, delivery_partners)
Admin    ──► [8.0 Generate Reports]     ◄── (orders, payments)

Delivery ──► [9.0 Accept & Dispatch]    ──► (orders)
Delivery ──► [10.0 Collect Payment]     ──► (payments)
```

---

## 13. Use Case Diagram
```
                       ┌────────────────────────────────────────┐
                       │          Petrol Buddy System           │
                       │                                        │
  ┌──────────┐         │  ○ Register / Login                    │
  │          │─────────┼─►○ Place Fuel Order (Petrol/Diesel)    │
  │ Customer │         │  ○ Detect Browser Geolocation          │
  │          │         │  ○ Track 5-Stage Delivery Timeline     │
  └──────────┘         │  ○ Cancel Unfulfilled Order            │
                       │  ○ Submit 5-Star Feedback              │
                       │  ○ Manage Personal Profile             │
                       │                                        │
  ┌──────────┐         │  ○ View Real-Time Dashboard Metrics    │
  │          │─────────┼─►○ Set Daily Petrol/Diesel Unit Prices │
  │  Admin   │         │  ○ Manage Fuel Stock Reserves          │
  │          │         │  ○ Confirm/Reject Customer Orders      │
  └──────────┘         │  ○ Assign Delivery Partners            │
                       │  ○ Audit Payments & Customer Feedback  │
                       │  ○ Print Sales Summary Reports         │
                       │                                        │
  ┌──────────┐         │  ○ Toggle Online Duty Status           │
  │ Delivery │─────────┼─►○ View Assigned Order Destination     │
  │ Partner  │         │  ○ Advance Status (Assigned->Out->Done)│
  └──────────┘         │  ○ Collect Cash on Delivery            │
                       └────────────────────────────────────────┘
```

---

## 14. Entity-Relationship (ER) Diagram
```
users (id, email, password, role, status, created_at)
  │
  ├── 1:1 ── customers (id, user_id [FK], full_name, phone, address, city, pincode)
  │             │
  │             └── 1:N ── orders (id, order_code, customer_id [FK], delivery_partner_id [FK],
  │                          │      fuel_type, quantity_litres, price_per_litre, total_amount,
  │                          │      delivery_address, city, pincode, landmark, latitude, longitude,
  │                          │      preferred_date, preferred_time, additional_instructions,
  │                          │      payment_method, status, rejection_reason, created_at)
  │                          │
  │                          ├── 1:1 ── payments (id, order_id [FK], payment_method, amount,
  │                          │                    payment_status, transaction_ref, payment_date)
  │                          │
  │                          └── 1:1 ── feedback (id, order_id [FK], customer_id [FK],
  │                                               rating, message, created_at)
  │
  ├── 1:1 ── admins (id, user_id [FK], full_name, phone)
  │
  └── 1:1 ── delivery_partners (id, user_id [FK], full_name, phone, address,
                                vehicle_number, is_available)
                │
                └── 1:N ── orders.delivery_partner_id [FK]

Standalone Lookup Tables:
- fuel_inventory (id, fuel_type [UNIQUE], available_litres, minimum_threshold, last_updated)
- fuel_prices    (id, fuel_type [UNIQUE], price_per_litre, effective_date)
```

---

## 15. Database Table Descriptions

| Table Name | Primary Key | Foreign Keys | Description |
|---|---|---|---|
| `users` | `id` | None | Master authentication table storing email, Werkzeug hashed password, role, and active status. |
| `customers` | `id` | `user_id` &rarr; `users.id` | Profile details for registered customers (name, phone, street, city, PIN). |
| `admins` | `id` | `user_id` &rarr; `users.id` | System administrator account attributes. |
| `delivery_partners` | `id` | `user_id` &rarr; `users.id` | Mobile Bowser pilot records, contact, vehicle reg number, and duty status. |
| `fuel_inventory` | `id` | None | Stores available litres and low-stock alert thresholds for Petrol and Diesel. |
| `fuel_prices` | `id` | None | Real-time selling price per litre for Petrol and Diesel. |
| `orders` | `id` | `customer_id` &rarr; `customers.id`<br>`delivery_partner_id` &rarr; `delivery_partners.id` | Central order transactions, location details, quantities, schedule, and statuses. |
| `payments` | `id` | `order_id` &rarr; `orders.id` | Financial ledger recording payment method, amounts, settlement statuses, and references. |
| `feedback` | `id` | `order_id` &rarr; `orders.id`<br>`customer_id` &rarr; `customers.id` | Verified ratings (1–5 stars) and review text submitted by customers. |

---

## 16. Module Descriptions

### 1. Public & Core Authentication Module (`routes/public.py`, `routes/auth.py`)
- Homepage featuring live fuel price tickers sourced directly from the database.
- Role-aware unified login with automatic post-login routing.
- Customer registration with transactional integrity.
- Custom template filters (`|currency`, `|fmt_date`, `|fmt_datetime`, `|stars`).

### 2. Customer Module (`routes/customer.py`)
- Dashboard displaying quick statistics (Total Orders, Active Orders, Delivered, Spent).
- Order form with dynamic JavaScript total calculation, stock threshold warnings, and HTML5 browser GPS coordinate capture.
- 5-stage visual delivery tracker with timeline nodes.
- In-place cancellation mechanism with database rollback.
- Interactive star-rating submission interface.

### 3. Administrator Module (`routes/admin.py`)
- KPI dashboard with real-time stock alert banners.
- Order management workflow with confirmation, partner assignment, and status controls.
- Inventory restocking and minimum safety threshold configuration.
- Daily fuel rate management.
- Partner onboarding and account state toggles.
- Filterable sales analytics with browser print optimization.

### 4. Delivery Partner Module (`routes/delivery.py`)
- Delivery assignment view with customer telephone links and street address details.
- Workflow progression: `Partner Assigned` &rarr; `Out for Delivery` &rarr; `Delivered`.
- COD settlement recording.
- Duty availability toggle (`Available` / `Unavailable`).

---

## 17. Testing and Test Cases

| Test Case ID | Test Scenario | Input Data | Expected Output | Status |
|---|---|---|---|---|
| **TC-01** | Customer Registration | Valid unique email, name, phone, password | Account created in DB, redirect to login | Pass |
| **TC-02** | Duplicate Email Registration | Existing registered email | Validation error: "Account already exists" | Pass |
| **TC-03** | Customer Authentication | Correct email & password | Session created, redirect to `/customer/dashboard` | Pass |
| **TC-04** | Invalid Password Login | Correct email, wrong password | Error: "Incorrect password" | Pass |
| **TC-05** | Unauthorized Role Access | Customer attempting `/admin/dashboard` | 403 / Redirect with flash error | Pass |
| **TC-06** | Place Fuel Order | 15L Petrol, valid address | Order created, stock deducted by 15L | Pass |
| **TC-07** | Order Exceeding Stock | 2000L Petrol when 1250L available | Error: "Insufficient stock available" | Pass |
| **TC-08** | Browser GPS Location | Click "Detect Location" button | Latitude & Longitude inputs populated | Pass |
| **TC-09** | Customer Order Cancellation | Cancel order in `Placed` status | Status &rarr; `Cancelled`, stock restored in DB | Pass |
| **TC-10** | Partner Status Transition | Partner marks `Out for Delivery` | Status updated in DB, reflected in tracker | Pass |
| **TC-11** | Delivery Completion & COD | Partner completes delivery | Status &rarr; `Delivered`, Payment &rarr; `Paid` | Pass |
| **TC-12** | Admin Daily Price Update | Petrol unit price set to ₹105.00 | New orders calculate at ₹105/L | Pass |

---

## 18. Advantages
1. **Convenience:** Consumers receive certified fuel at their doorstep without traveling or queueing.
2. **Emergency Support:** Motorists stranded on roadsides can request on-demand refueling.
3. **Generator Safety:** Eliminates the hazardous practice of carrying fuel in unapproved plastic jerrycans.
4. **Zero Paid APIs:** Operates cleanly using built-in browser APIs and local MySQL without external costs.
5. **Data Consistency:** Database transactions prevent inventory discrepancies during order placement and cancellation.
6. **Academic Suitability:** Well-structured Python codebase demonstrating modern MVC concepts, RESTful route separation, and database normalization.

---

## 19. Limitations
1. **Simulation Scope:** Online payments are simulated for academic demonstration and do not connect to live banking gateways.
2. **Offline Geolocation:** Coordinates are captured via the browser HTML5 API without an embedded interactive map visualizer.
3. **Notification System:** Status updates are stored in the database; real-time SMS/push notifications are not implemented.

---

## 20. Future Enhancements
1. **Interactive Map Integration:** Incorporate Leaflet.js and OpenStreetMap for live Bowser route visualization.
2. **Payment Gateway Integration:** Connect Razorpay / Stripe sandbox for real card and UPI processing.
3. **SMS Alerts:** Integrate Twilio or Fast2SMS for dispatch and delivery notifications.
4. **Mobile Application:** Develop companion Flutter / React Native mobile apps for customers and delivery pilots.
5. **Multi-Depot Routing:** Support inventory distribution across multiple regional fuel depots.

---

## 21. Conclusion
The **Petrol Buddy – Online Petrol Delivery System** demonstrates a full-stack web application built with **Python (Flask)** and **MySQL**. It addresses real-world logistical challenges surrounding fuel procurement by uniting customers, administrators, and delivery pilots on a centralized platform. The project showcases essential software engineering practices: role-based access control, parameterized database interaction, atomic transactional workflows, responsive styling, and complete offline operability.

---

*Designed & Developed by **Pardhu** | College Mini-Project Technical Report*
