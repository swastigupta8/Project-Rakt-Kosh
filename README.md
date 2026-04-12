## 🩸 Rakt-Kosh | Real-Time Blood Inventory & Donor Network

![React](https://img.shields.io/badge/React-19-blue?style=flat&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-Python-009688?style=flat&logo=fastapi)
![MySQL](https://img.shields.io/badge/MySQL-Spatial-4479A1?style=flat&logo=mysql)

**Rakt-Kosh** is a full-stack Database Management System (DBMS) tailored for the Indian healthcare landscape. It digitizes the blood donation lifecycle to streamline inventory tracking, automate medical expiration protocols, and utilize geospatial data to instantly connect patients with the nearest available blood drives and hospital inventories.

### 📄 Comprehensive 42-Page Documentation
Read the full academic project report, which includes complete database schemas, ER diagrams, 3NF normalization breakdowns, and spatial query performance analysis.

*(Note: To view the documentation locally, open `DBS Project Report.pdf` located in the root directory).*

## ✨ Core Features
* **Geospatial Proximity Engine:** Utilizes MySQL's `ST_Distance_Sphere` function and the Geopy/Nominatim API to instantly match patients with the ten nearest active donation drives or hospitals.
* **Automated Expiry & Eligibility Logic:** Features backend background tasks (`APScheduler`) that enforce the strict 42-day blood expiry protocol and monitor the 56-day donor recuperation window.
* **Role-Based Access Control (RBAC):** A secure, dual-portal interface separating the Patient/Donor workflows from Hospital Administrative tools.
* **Live Inventory Tracking:** Allows hospitals to update stock in real-time, preventing the life-threatening information asymmetry found in decentralized systems.

## 🛠️ Technology Stack
* **Frontend:** React 19, Vite, React Router DOM v7, Context API, CSS3
* **Backend:** Python, FastAPI, Pydantic, APScheduler
* **Database:** MySQL (Relational architecture with Spatial Functions)
* **Authentication:** Passlib (bcrypt hashing)
* **Geocoding:** Nominatim (OpenStreetMap API)

## 🚀 Local Installation & Setup

Follow these steps to run the Rakt-Kosh environment locally on your machine. Ensure you have **Node.js**, **Python 3.8+**, and **MySQL** installed.

### 1. Database Setup
1. Open your MySQL interface (e.g., MySQL Workbench).
2. Create a new database: `CREATE DATABASE raktkosh;`
3. Use the database: `USE raktkosh;`
4. **Execute** your schema scripts to build the relational tables:
```sql
-- Core tables required:
-- 1. BloodBanks
-- 2. Users (Includes City, Latitude, Longitude)
-- 3. BloodInventory
-- 4. DonationDrives
-- 5. BloodRequests
```

### 2. Backend (FastAPI) Setup
Open a terminal, navigate to your backend directory, and run the following commands:
```bash
# Install all required Python dependencies
pip install fastapi uvicorn mysql-connector-python passlib bcrypt geopy apscheduler

# Start the FastAPI server
uvicorn main:app --reload
```
*The API will be live at `http://127.0.0.1:8000`*

### 3. Frontend (React) Setup
Open a **second terminal window**, navigate to your frontend directory, and run:
```bash
# Install Node modules
npm install

# Start the Vite development server
npm run dev
```
*The web interface will be live at `http://localhost:5173`*

## 💡 System Architecture
Rakt-Kosh follows a clean **Three-Tier Architecture**. The React presentation layer utilizes asynchronous Axios calls to communicate with the FastAPI application layer. The backend processes the business logic—such as bcrypt password verification and geographic coordinate extraction—before interacting with the MySQL data layer using raw, parameterized SQL queries to prevent injection attacks.
```
