from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from geopy.geocoders import Nominatim
from pydantic import BaseModel  # <-- STEP 1: NEW IMPORT
from datetime import date       # <-- STEP 1: NEW IMPORT
from passlib.context import CryptContext
from datetime import date, time
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager

# 1. Database Connection String
# REPLACE 'YOUR_PASSWORD_HERE' with your actual MySQL root password!
DATABASE_URL = "mysql+pymysql://root:swasti@localhost/projectraktkosh"
engine = create_engine(DATABASE_URL)

# 2. Initialize the FastAPI App
# Setup the background scheduler
scheduler = BackgroundScheduler()

# This tells FastAPI what to do when it turns on and turns off
@asynccontextmanager
async def lifespan(app: FastAPI):
    # What happens when the server STARTS:
    # For testing, we are telling it to run every 10 seconds!
    # (In production, you would change this to run once a day at midnight)
    scheduler.add_job(check_donation_eligibility, 'interval', seconds=600)
    scheduler.start()
    print("⏰ Background Scheduler Started!")
    
    yield # This means "let the server run normally now"
    
    # What happens when the server STOPS:
    scheduler.shutdown()
    print("⏰ Background Scheduler Stopped!")

# Initialize the FastAPI App with the lifespan attached
app = FastAPI(title="Raktkosh Backend API", lifespan=lifespan)

# Allow the React frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Geocoder
geolocator = Nominatim(user_agent="raktkosh_blood_bank_app")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# ==========================================
# <-- STEP 2: THIS IS EXACTLY WHERE IT GOES 
# (Below setup, above the endpoints)
# ==========================================
class BloodInventoryCreate(BaseModel):
    BankID: int
    BloodGroup: str
    CollectionDate: date

class UserCreate(BaseModel):
    FullName: str
    Email: str
    Password: str
    PhoneNumber: str
    BloodGroup: str
    City: str

class UserLogin(BaseModel):
    Email: str
    Password: str

class DonationDriveCreate(BaseModel):
    BankID: int
    DriveName: str
    DriveDate: date
    StartTime: time
    EndTime: time
    City: str  

class BloodRequestCreate(BaseModel):
    UserID: int
    BloodGroup: str
    UnitsRequired: int

class BankCreate(BaseModel):
    Name: str
    GovtRegistrationNo: str
    ContactEmail: str
    Password: str
    ContactPhone: str
    City: str
    Address: str

# ==========================================
# BACKGROUND AUTOMATION TASKS
# ==========================================

def check_donation_eligibility():
    """Checks the database for users who donated exactly 56 days ago."""
    print("\n[SYSTEM] Running daily 56-day eligibility check...")
    
    try:
        with engine.connect() as connection:
            # Query users where exactly 56 days have passed since LastDonationDate
            query = text("""
                SELECT FullName, Email 
                FROM Users 
                WHERE LastDonationDate IS NOT NULL 
                AND DATEDIFF(CURRENT_DATE, LastDonationDate) = 56
            """)
            
            eligible_users = connection.execute(query).fetchall()
            
            if not eligible_users:
                print("[SYSTEM] No users are hitting their 56-day mark today.")
                return

            for user in eligible_users:
                name = user[0]
                email = user[1]
                # In the future, you would trigger an actual email API (like SendGrid) here
                print(f"📧 [EMAIL SENT] To: {email} | Message: Hi {name}, it's been 56 days! You can save another life today.")
                
    except Exception as e:
        print(f"[SYSTEM ERROR] Failed to run background task: {e}")

# ==========================================
# 3. ENDPOINTS START HERE
# ==========================================

# Health Check
@app.get("/")
def read_root():
    return {"message": "Welcome to the Raktkosh Blood Bank API! The server is running."}

# Find Nearest Drives
@app.get("/api/nearest-drives")
def get_nearest_drives(city: str):
    try:
        location = geolocator.geocode(city, country_codes="IN")
        if not location:
            raise HTTPException(status_code=404, detail="City not found. Please try a different name.")
            
        user_lat = location.latitude
        user_lng = location.longitude

        with engine.connect() as connection:
            query = text("""
                SELECT DriveName, DriveDate, Address, StartTime, EndTime,
                       ST_Distance_Sphere(point(Longitude, Latitude), point(:lng, :lat)) AS DistanceMeters
                FROM DonationDrives
                ORDER BY DistanceMeters ASC
                LIMIT 10;
            """)
            
            result = connection.execute(query, {"lat": user_lat, "lng": user_lng})
            
            drives = []
            for row in result:
                drives.append({
                    "name": row[0],
                    "date": str(row[1]),
                    "address": row[2],
                    "time": f"{row[3]} - {row[4]}",
                    "distance_km": round(row[5] / 1000, 2) if row[5] else None
                })
                
            return {
                "status": "success", 
                "searched_location": {"city": city, "lat": user_lat, "lng": user_lng},
                "data": drives
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# <-- STEP 3: THE NEW POST ENDPOINT GOES AT THE VERY BOTTOM
@app.post("/api/inventory/add")
def add_blood_inventory(inventory: BloodInventoryCreate):
    try:
        valid_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        if inventory.BloodGroup not in valid_groups:
            raise HTTPException(status_code=400, detail="Invalid Blood Group")

        with engine.connect() as connection:
            query = text("""
                INSERT INTO BloodInventory (BankID, BloodGroup, CollectionDate, Status)
                VALUES (:bank_id, :blood_group, :collection_date, 'Available')
            """)
            
            connection.execute(query, {
                "bank_id": inventory.BankID,
                "blood_group": inventory.BloodGroup,
                "collection_date": inventory.CollectionDate
            })
            
            connection.commit() 
            
            return {"status": "success", "message": f"{inventory.BloodGroup} blood bag added successfully!"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# 6. Register a New User
@app.post("/api/users/register")
def register_user(user: UserCreate):
    try:
        # 1. Validate Blood Group
        valid_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        if user.BloodGroup not in valid_groups:
            raise HTTPException(status_code=400, detail="Invalid Blood Group")

        # 2. Convert City to Coordinates using Geopy
        location = geolocator.geocode(user.City, country_codes="IN")
        if not location:
            raise HTTPException(status_code=400, detail="Could not find city. Please try again.")
            
        user_lat = location.latitude
        user_lng = location.longitude

        # 3. Hash the Password securely
        hashed_password = get_password_hash(user.Password)

        # 4. Save to Database
        with engine.connect() as connection:
            # Make sure City is in the INSERT statement!
            query = text("""
                INSERT INTO Users (FullName, Email, PasswordHash, PhoneNumber, BloodGroup, Latitude, Longitude, City)
                VALUES (:FullName, :Email, :PasswordHash, :PhoneNumber, :BloodGroup, :Latitude, :Longitude, :City)
            """)
            # Make sure the dictionary keys exactly match the :Variables in the query above!
            connection.execute(query, {
                "FullName": user.FullName,
                "Email": user.Email,
                "PasswordHash": hashed_password,  
                "PhoneNumber": user.PhoneNumber,
                "BloodGroup": user.BloodGroup,
                "Latitude": user_lat,  # Fixed: Now using user_lat!
                "Longitude": user_lng, # Fixed: Now using user_lng!
                "City": user.City      
            })
        
            connection.commit() # Don't forget to save!
            
            return {"status": "success", "message": f"User {user.FullName} registered successfully!"}
            
    except Exception as e:
        # This catches errors like trying to register an email that already exists
        if "Duplicate entry" in str(e):
            raise HTTPException(status_code=400, detail="Email or Phone Number already registered.")
        raise HTTPException(status_code=500, detail=str(e))

# 6b. Register a New Blood Bank
@app.post("/api/banks/register")
def register_bank(bank: BankCreate):
    try:
        # Convert City/Address to Coordinates
        location = geolocator.geocode(f"{bank.Address}, {bank.City}", country_codes="IN")
        if not location:
            # Fallback to just city if exact address fails
            location = geolocator.geocode(bank.City, country_codes="IN")
            if not location:
                raise HTTPException(status_code=400, detail="Could not find location. Please verify city/address.")
            
        bank_lat = location.latitude
        bank_lng = location.longitude

        # Hash the Password securely
        hashed_password = get_password_hash(bank.Password)

        with engine.connect() as connection:
            query = text("""
                INSERT INTO BloodBanks (Name, GovtRegistrationNo, ContactEmail, PasswordHash, ContactPhone, Latitude, Longitude, City, Address)
                VALUES (:Name, :GovtNo, :Email, :PasswordHash, :Phone, :Latitude, :Longitude, :City, :Address)
            """)
            connection.execute(query, {
                "Name": bank.Name,
                "GovtNo": bank.GovtRegistrationNo,
                "Email": bank.ContactEmail,
                "PasswordHash": hashed_password,  
                "Phone": bank.ContactPhone,
                "Latitude": bank_lat,  
                "Longitude": bank_lng, 
                "City": bank.City,
                "Address": bank.Address
            })
            connection.commit()
            
            return {"status": "success", "message": f"Hospital '{bank.Name}' registered successfully!"}
            
    except Exception as e:
        if "Duplicate entry" in str(e):
            raise HTTPException(status_code=400, detail="Email or Registration Number already exists.")
        raise HTTPException(status_code=500, detail=str(e))

# 7. Unified Login (For Both Users and Banks)
@app.post("/api/users/login")
def login_unified(credentials: UserLogin):
    try:
        with engine.connect() as connection:
            # First, check if it's a regular USER
            user_query = text("SELECT UserID, FullName, PasswordHash FROM Users WHERE Email = :email")
            user_result = connection.execute(user_query, {"email": credentials.Email}).fetchone()

            if user_result:
                # It's a user! Verify password.
                if not verify_password(credentials.Password, user_result[2]):
                    raise HTTPException(status_code=401, detail="Invalid email or password")
                
                return {
                    "status": "success", 
                    "message": f"Welcome back, {user_result[1]}!", 
                    "role": "user",           # <-- Tells React this is a Patient/Donor
                    "id": user_result[0]      
                }

            # If not a user, check if it's a BLOOD BANK
            bank_query = text("SELECT BankID, Name, PasswordHash FROM BloodBanks WHERE ContactEmail = :email")
            bank_result = connection.execute(bank_query, {"email": credentials.Email}).fetchone()

            if bank_result:
                # It's a bank! Verify password.
                if not verify_password(credentials.Password, bank_result[2]):
                    raise HTTPException(status_code=401, detail="Invalid email or password")
                
                return {
                    "status": "success", 
                    "message": f"Hospital Portal Access: {bank_result[1]}", 
                    "role": "bank",           # <-- Tells React this is an Admin
                    "id": bank_result[0]      
                }

            # If the email isn't in EITHER table:
            raise HTTPException(status_code=401, detail="Invalid email or password")

    except HTTPException:
        raise 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# 8. Schedule a New Donation Drive
@app.post("/api/drives/new")
def create_donation_drive(drive: DonationDriveCreate):
    try:
        # Convert the drive's city into coordinates
        location = geolocator.geocode(drive.City, country_codes="IN")
        if not location:
            raise HTTPException(status_code=400, detail="Could not find city for the drive.")
            
        drive_lat = location.latitude
        drive_lng = location.longitude

        with engine.connect() as connection:
            query = text("""
                INSERT INTO DonationDrives (BankID, DriveName, DriveDate, StartTime, EndTime, Latitude, Longitude, Address)
                VALUES (:bank_id, :name, :date, :start, :end, :lat, :lng, :address)
            """)
            
            connection.execute(query, {
                "bank_id": drive.BankID,
                "name": drive.DriveName,
                "date": drive.DriveDate,
                "start": drive.StartTime,
                "end": drive.EndTime,
                "lat": drive_lat,
                "lng": drive_lng,
                "address": drive.City # Saving the city name as the base address
            })
            connection.commit()
            
            return {"status": "success", "message": f"Drive '{drive.DriveName}' scheduled successfully!"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 9. Request Blood (For Patients)
@app.post("/api/requests/new")
def create_blood_request(request: BloodRequestCreate):
    try:
        valid_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        if request.BloodGroup not in valid_groups:
            raise HTTPException(status_code=400, detail="Invalid Blood Group")

        if request.UnitsRequired <= 0:
            raise HTTPException(status_code=400, detail="Must request at least 1 unit.")

        with engine.connect() as connection:
            query = text("""
                INSERT INTO BloodRequests (UserID, BloodGroup, UnitsRequired, Status)
                VALUES (:user_id, :blood_group, :units, 'Pending')
            """)
            
            connection.execute(query, {
                "user_id": request.UserID,
                "blood_group": request.BloodGroup,
                "units": request.UnitsRequired
            })
            connection.commit()
            
            return {"status": "success", "message": f"Request for {request.UnitsRequired} units of {request.BloodGroup} submitted."}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# 10. View Pending Blood Requests (For Blood Banks - SORTED BY DISTANCE)
@app.get("/api/requests/pending/{bank_id}")
def get_pending_requests(bank_id: int):
    try:
        with engine.connect() as connection:
            # We join the Requests, the Users (to get patient coordinates), 
            # and the BloodBank (to get the viewing hospital's coordinates)
            query = text("""
                SELECT r.RequestID, u.FullName, u.PhoneNumber, u.City, r.BloodGroup, r.UnitsRequired, r.RequestDate,
                       ST_Distance_Sphere(point(u.Longitude, u.Latitude), point(b.Longitude, b.Latitude)) AS DistanceMeters
                FROM BloodRequests r
                JOIN Users u ON r.UserID = u.UserID
                JOIN BloodBanks b ON b.BankID = :bank_id
                WHERE r.Status = 'Pending'
                ORDER BY DistanceMeters ASC, r.RequestDate DESC
            """)
            
            results = connection.execute(query, {"bank_id": bank_id}).fetchall()
            
            request_list = []
            for row in results:
                # Convert the distance from meters to kilometers
                distance_km = round(row[7] / 1000, 1) if row[7] is not None else 0
                
                request_list.append({
                    "RequestID": row[0],
                    "PatientName": row[1],
                    "Phone": row[2],
                    "City": row[3],
                    "BloodGroup": row[4],
                    "Units": row[5],
                    "Date": str(row[6]),
                    "DistanceKM": distance_km
                })
                
            return {"status": "success", "data": request_list}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 12. Search Available Blood by Distance (For Patients)
@app.get("/api/inventory/search")
def search_blood(blood_group: str, city: str):
    try:
        # 1. Geocode the patient's searched city
        location = geolocator.geocode(city, country_codes="IN")
        if not location:
            raise HTTPException(status_code=404, detail="City not found. Please try again.")
            
        search_lat = location.latitude
        search_lng = location.longitude

        with engine.connect() as connection:
            # 2. The Super-Query: Join Inventory + Banks + Spatial Math
            query = text("""
                SELECT b.Name, b.ContactPhone, b.Address, i.BloodBagID, i.CollectionDate,
                       ST_Distance_Sphere(point(b.Longitude, b.Latitude), point(:lng, :lat)) AS DistanceMeters
                FROM ActiveBloodInventory i
                JOIN BloodBanks b ON i.BankID = b.BankID
                WHERE i.BloodGroup = :blood_group 
                AND i.CurrentStatus = 'Available'
                ORDER BY DistanceMeters ASC
            """)
            
            # Note: We must replace the '+' in blood groups if passed via URL, 
            # but FastAPI handles standard decoding. We just ensure exact match.
            results = connection.execute(query, {
                "blood_group": blood_group,
                "lat": search_lat,
                "lng": search_lng
            }).fetchall()
            
            search_results = []
            for row in results:
                search_results.append({
                    "HospitalName": row[0],
                    "Phone": row[1],
                    "Address": row[2],
                    "BagID": row[3],
                    "CollectionDate": str(row[4]),
                    "DistanceKM": round(row[5] / 1000, 2) if row[5] else None
                })
                
            return {
                "status": "success", 
                "searched_location": {"city": city, "lat": search_lat, "lng": search_lng},
                "data": search_results
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 11. View Live Inventory (For Blood Banks)
@app.get("/api/inventory/{bank_id}")
def get_bank_inventory(bank_id: int):
    try:
        with engine.connect() as connection:
            # We are querying your awesome ActiveBloodInventory VIEW here!
            query = text("""
                SELECT BloodBagID, BloodGroup, CollectionDate, CurrentStatus
                FROM ActiveBloodInventory
                WHERE BankID = :bank_id
                ORDER BY CollectionDate DESC
            """)
            
            results = connection.execute(query, {"bank_id": bank_id}).fetchall()
            
            inventory_list = []
            for row in results:
                inventory_list.append({
                    "BloodBagID": row[0],
                    "BloodGroup": row[1],
                    "CollectionDate": str(row[2]),
                    "Status": row[3]
                })
                
            return {"status": "success", "data": inventory_list}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
