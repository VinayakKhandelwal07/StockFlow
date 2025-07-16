# 📦 StockFlow - Inventory Management System

StockFlow is a full-featured, Django-based inventory management system designed for production use. It enables businesses to efficiently manage products, users, inventory stock levels, and get insights into their operations through a clean dashboard interface.

---

## 🚀 Features

-  🔐 User Authentication & Registration
- 🏢 Multi-Company Tenancy (Tenant isolation)
- 👥 Role-Based Access Control (Admin, Manager, Staff)
- 📦 Inventory & Product Management
- 📝 Order Request & Approval Workflow
- 🧾 Real-Time Stock Updates
- 📊 Dynamic Dashboards per Company
- 📨 Email Notifications (Gmail SMTP integration)
- 💬 Contact Form with Email Delivery
- 🧑‍💼 User Profile & First Login Password Enforcement
- 🛠️ Modular Django App Structure
- 🖥️ Responsive UI (Bootstrap 4 + Crispy Forms)
- 🗃️ PostgreSQL Database Support
- 🧾 Logging & Audit Trails for Orders and User Actions
- ✅ Secure, Validated Order State Machine
- ⚙️ Transactional Atomicity for Critical Operations


## 🧠 Project Overview

StockFlow is built for organizations needing multi-role inventory systems with isolated company data. It ensures each business (tenant) can operate independently while sharing a single deployed application instance.

### 🌐 Multi-Tenant Architecture

- Each registered company acts as a **separate tenant**.
- Data isolation ensures users can only access resources within their company.
- Super Admin or platform owner manages onboarding, while each company manages its own users.

### 👥 User Roles

| Role   | Capabilities |
|--------|--------------|
| Admin  | Full company-level access: manage users, inventory, view all data |
| Manager | Approve/Reject order requests, manage stock |
| Staff  | Create requests(Restock Or Customer Order), view their own requests, update profile |

---
## 🧾 Order Management Workflow

1. **Request Creation** (by Staff)
2. **Approval/Rejection** (by Manager)
3. **Order Confirmation** – triggers automatic stock update
4. **Audit Logging** for all transitions and actions

### 🔄 Request Lifecycle Controls

- Staff cannot modify/delete requests after manager approval.
- Order states are strictly validated and enforced (Pending → Approved → Fulfilled).

---
## 🐳 Deployment & DevOps

To prepare for deployment:

1. **Dockerization** (Coming Soon)
2. **CI/CD Pipelines** – Integrate GitHub Actions or GitLab CI for testing & deployment
3. **Environment Variables** – Store credentials & keys securely
4. **HTTPS & Domain Setup** – Production-ready hosting via Heroku, AWS, or DigitalOcean

---
## 🛠️ Tech Stack

- **Backend**: Django 4.x
- **Frontend**: Bootstrap 4, Crispy Forms
- **Database**: PostgreSQL
- **Email**: Gmail SMTP
- **Auth**: Django User Model + Custom Roles
- **Logging**: Django signals & middleware

---
📄 License

This project is licensed under the MIT License.

---

📬 Contact

Have questions or suggestions?

📧 Email: stockflowhello@gmail.com
🌐 Website: Coming Soon

---


👨‍💻 Developed By

Vinayak Khandelwal

📧 Email: vinayakkhandelwal34@gmail.com

---
