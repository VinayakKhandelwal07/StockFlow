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
- 

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
| Staff  | Create requests, view assigned inventory, update profile |

---


---
