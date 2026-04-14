# 🩸 Rakt-Kosh | Real-Time Blood Inventory & Donor Network

A full-stack healthcare platform designed to digitize the blood donation lifecycle, enabling real-time inventory tracking, automated medical compliance, and geospatial matching between patients and nearby blood sources.

---

## 🚀 Key Highlights

- Real-time blood inventory management across hospitals  
- Geospatial matching of patients with nearest donation drives and blood banks  
- Automated enforcement of blood expiry (42 days) and donor eligibility (56 days)  
- Secure role-based access for patients, donors, and hospital administrators  

---

## 🧠 System Overview

Rakt-Kosh follows a **three-tier architecture**:

1. **Frontend (React)**  
   Handles user interaction, dashboards, and API communication  

2. **Backend (FastAPI)**  
   Processes business logic, authentication, and scheduling tasks  

3. **Database (MySQL)**  
   Stores relational data with spatial indexing for geolocation queries  

---

## ⚙️ How It Works

1. Users register as donors, patients, or hospital admins  
2. Hospitals update blood inventory in real time  
3. Backend enforces:
   - Blood expiry tracking (42 days)  
   - Donor recovery window (56 days)  
4. Patients are matched with the **nearest available blood sources** using geospatial queries  
5. Results are displayed instantly via the frontend dashboard  

---

## 🛠️ Tech Stack

**Frontend:** React, Vite, React Router, CSS  
**Backend:** FastAPI, Python, Pydantic, APScheduler  
**Database:** MySQL (Relational + Spatial Functions)  
**Authentication:** Passlib (bcrypt)  
**Geocoding:** OpenStreetMap (Nominatim API)  

---

## 🧩 Core Features

### 📍 Geospatial Matching Engine
- Uses MySQL spatial functions (`ST_Distance_Sphere`)  
- Integrates with OpenStreetMap API for real-world coordinates  
- Returns nearest hospitals and donation drives  

### ⏱️ Automated Medical Logic
- Tracks blood expiry (42-day lifecycle)  
- Enforces donor eligibility window (56 days)  
- Runs scheduled background jobs using APScheduler  

### 🔐 Role-Based Access Control
- Separate workflows for:
  - Patients / Donors  
  - Hospital Administrators  
- Ensures secure and structured data access  

### 📊 Live Inventory Tracking
- Real-time updates to blood stock levels  
- Eliminates outdated or inconsistent availability data  

---

## 🏗️ Database Design

- Fully normalized relational schema (up to 3NF)  
- Core tables include:
  - Users  
  - BloodInventory  
  - BloodBanks  
  - DonationDrives  
  - BloodRequests  
- Optimized queries using indexing and parameterized SQL  

---

## 📸 Screenshots

<img width="1160" height="627" alt="image" src="https://github.com/user-attachments/assets/75c678a2-5286-4fea-b89e-c6626207132c" />
<img width="1161" height="618" alt="image" src="https://github.com/user-attachments/assets/2e5c9a5b-5a53-4186-80de-1b584b588f38" />
<img width="1161" height="622" alt="image" src="https://github.com/user-attachments/assets/43158b9b-87b7-4066-8c1c-7c0f026d5653" />
<img width="1163" height="627" alt="image" src="https://github.com/user-attachments/assets/c986ee17-f584-4294-ad62-67807d79388d" />
<img width="1147" height="621" alt="image" src="https://github.com/user-attachments/assets/d0ffc00a-9945-4a33-ba02-4e78100c124f" />
<img width="1154" height="620" alt="image" src="https://github.com/user-attachments/assets/4a37a957-e8b4-43ab-98c7-0b80bb988a31" />
<img width="1158" height="619" alt="image" src="https://github.com/user-attachments/assets/f7ea7eaf-404e-4cbc-88fd-ca30c8b6981e" />
<img width="1152" height="617" alt="image" src="https://github.com/user-attachments/assets/fe2346e1-ff50-40aa-8483-805f7476d151" />
<img width="1152" height="622" alt="image" src="https://github.com/user-attachments/assets/00ff479f-a9dd-46f3-8eed-73486c5d6bcd" />
<img width="1152" height="626" alt="image" src="https://github.com/user-attachments/assets/97ad8abc-d6d4-4000-a0e0-a75947f0c65a" />

---

## 🚀 Getting Started

### 1. Clone the repository
git clone https://github.com/swastigupta8/Project-Rakt-Kosh.git
cd Project-Rakt-Kosh
### 2. Setup Backend
pip install fastapi uvicorn mysql-connector-python passlib bcrypt geopy apscheduler
uvicorn main:app --reload
### 3. Setup Frontend
npm install
npm run dev

# #🎯 Impact

Rakt-Kosh addresses critical inefficiencies in decentralized blood management systems by:

Reducing delays in emergency blood access
Improving transparency in hospital inventory
Automating compliance with medical safety protocols

## 📄 Documentation

This project includes a detailed 42-page technical report covering:

ER diagrams
Schema design
Normalization (3NF)
Query optimization and performance analysis

## 👩‍💻 Author

Swasti Gupta
Computer Science Undergraduate, Manipal Institute of Technology
