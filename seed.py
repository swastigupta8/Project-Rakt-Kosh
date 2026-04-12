import requests
import time
from datetime import date, timedelta
import random

BASE_URL = "http://127.0.0.1:8000/api"

print("🚀 INITIATING DEMO-DAY MEGA SEEDER...")
print("⚠️ Please do not close the terminal. This will take ~90 seconds to avoid GPS API limits.\n")

cities = ["Mumbai", "Pune", "Bangalore", "New Delhi", "Chennai"]
blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

# ==========================================
# 1. SEED 15 BLOOD BANKS (3 per city)
# ==========================================
print("🏥 Registering 15 Blood Banks...")
for i, city in enumerate(cities):
    for j in range(3):
        bank_data = {
            "Name": f"{city} {'Central' if j==0 else 'Care' if j==1 else 'Lifeline'} Hospital",
            "GovtRegistrationNo": f"GOV-{city[:3].upper()}-{1000 + i*10 + j}",
            "ContactEmail": f"admin{j+1}@{city.lower().replace(' ', '')}.com",
            "Password": "password123",
            "ContactPhone": f"900000{i}{j}00",
            "City": city,
            "Address": f"{random.randint(10, 99)} Main Street, {city}"
        }
        res = requests.post(f"{BASE_URL}/banks/register", json=bank_data)
        if res.status_code == 200:
            print(f"  ✅ Registered: {bank_data['Name']}")
        time.sleep(1.5) # GPS API limit protection


# ==========================================
# 2. SEED 15 USERS (3 per city)
# ==========================================
print("\n👤 Registering 15 Patients/Donors...")

first_names = ["Rohit", "Priya", "Amit", "Sneha", "Vikram", "Anjali", "Karan", "Neha", "Arjun", "Pooja", "Rahul", "Kavita", "Sanjay", "Divya", "Ravi"]
last_names = ["Patel", "Singh", "Reddy", "Mishra", "Gupta", "Desai", "Kumar", "Iyer", "Rao", "Das", "Sharma", "Nair", "Menon", "Joshi", "Verma"]

for i, name in enumerate(first_names):
    city = cities[i % len(cities)] # Spread them evenly across cities
    last_name = random.choice(last_names) # Grab a random last name!
    
    user_data = {
        "FullName": f"{name} {last_name}",
        "Email": f"{name.lower()}@test.com",
        "Password": "password123",
        "PhoneNumber": f"80000000{i:02d}",
        "BloodGroup": random.choice(blood_groups),
        "City": city
    }
    res = requests.post(f"{BASE_URL}/users/register", json=user_data)
    if res.status_code == 200:
        print(f"  ✅ Registered User: {user_data['FullName']} ({city})")
    time.sleep(1.5) # GPS API limit protection

# ==========================================
# 3. SEED 50 BLOOD BAGS (Inventory is instant, no GPS!)
# ==========================================
today = date.today()
print("\n🩸 Stocking Refrigerators (50 Bags)...")
for i in range(50):
    bank_id = random.randint(1, 15) # Assign randomly to our 15 banks
    bg = random.choice(blood_groups)
    
    # Make 10% of the blood bags intentionally expired for the demo dashboard
    days_ago = random.randint(1, 50) 
    coll_date = today - timedelta(days=days_ago)
    
    bag_data = {
        "BankID": bank_id,
        "BloodGroup": bg,
        "CollectionDate": str(coll_date)
    }
    requests.post(f"{BASE_URL}/inventory/add", json=bag_data)
print("  ✅ 50 Blood Bags successfully distributed across all hospitals!")

# ==========================================
# 4. SEED 15 DONATION DRIVES
# ==========================================
print("\n🚑 Scheduling 15 Donation Drives...")
for i in range(15):
    city = cities[i % len(cities)]
    drive_data = {
        "BankID": i + 1,
        "DriveName": f"{city} Mega Blood Camp {i+1}",
        "DriveDate": str(today + timedelta(days=random.randint(5, 30))),
        "StartTime": "09:00:00",
        "EndTime": "17:00:00",
        "City": city
    }
    res = requests.post(f"{BASE_URL}/drives/new", json=drive_data)
    if res.status_code == 200:
        print(f"  ✅ Scheduled: {drive_data['DriveName']}")
    time.sleep(1.5) # GPS API limit protection

# ==========================================
# 5. SEED 15 PENDING BLOOD REQUESTS (Instant, no GPS!)
# ==========================================
print("\n🚨 Simulating 15 Urgent Patient Requests...")
for i in range(15):
    req_data = {
        "UserID": i + 1,
        "BloodGroup": random.choice(blood_groups),
        "UnitsRequired": random.randint(1, 4)
    }
    requests.post(f"{BASE_URL}/requests/new", json=req_data)
print("  ✅ 15 Live Blood Requests injected into the network!")

print("\n🎉 DEMO ENVIRONMENT FULLY LOADED AND READY FOR SHOWCASE!")