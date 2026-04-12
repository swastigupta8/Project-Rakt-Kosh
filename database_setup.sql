-- 1. Create and select the database
CREATE DATABASE projectraktkosh;
USE projectraktkosh;

-- 2. Users Table (Handles both Donors and Recipients)
CREATE TABLE Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    FullName VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    PhoneNumber VARCHAR(15) UNIQUE NOT NULL,
    BloodGroup VARCHAR(3) NOT NULL,
    Latitude DECIMAL(10, 8) NOT NULL,
    Longitude DECIMAL(11, 8) NOT NULL,
    LastDonationDate DATE,
    CONSTRAINT chk_user_blood_group CHECK (BloodGroup IN ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'))
);

-- 3. Blood Banks Table
CREATE TABLE BloodBanks (
    BankID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(150) NOT NULL,
    GovtRegistrationNo VARCHAR(50) UNIQUE NOT NULL,
    ContactEmail VARCHAR(100) UNIQUE NOT NULL,
    ContactPhone VARCHAR(15) NOT NULL,
    Latitude DECIMAL(10, 8) NOT NULL,
    Longitude DECIMAL(11, 8) NOT NULL,
    Address TEXT NOT NULL
);

-- 4. Blood Inventory Table
CREATE TABLE BloodInventory (
    BloodBagID INT AUTO_INCREMENT PRIMARY KEY,
    BankID INT NOT NULL,
    BloodGroup VARCHAR(3) NOT NULL,
    CollectionDate DATE NOT NULL,
    Status VARCHAR(20) DEFAULT 'Available',
    FOREIGN KEY (BankID) REFERENCES BloodBanks(BankID) ON DELETE CASCADE,
    CONSTRAINT chk_inv_blood_group CHECK (BloodGroup IN ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')),
    CONSTRAINT chk_status CHECK (Status IN ('Available', 'Reserved', 'Used', 'Expired'))
);

-- 5. Donation Drives Table
CREATE TABLE DonationDrives (
    DriveID INT AUTO_INCREMENT PRIMARY KEY,
    BankID INT NOT NULL,
    DriveName VARCHAR(150) NOT NULL,
    DriveDate DATE NOT NULL,
    StartTime TIME NOT NULL,
    EndTime TIME NOT NULL,
    Latitude DECIMAL(10, 8) NOT NULL,
    Longitude DECIMAL(11, 8) NOT NULL,
    Address TEXT NOT NULL,
    FOREIGN KEY (BankID) REFERENCES BloodBanks(BankID) ON DELETE CASCADE
);

-- 6. Blood Requests Table (For users looking for blood)
CREATE TABLE BloodRequests (
    RequestID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT NOT NULL,
    BloodGroup VARCHAR(3) NOT NULL,
    RequestDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    UnitsRequired INT NOT NULL,
    Status VARCHAR(20) DEFAULT 'Pending',
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE,
    CONSTRAINT chk_req_status CHECK (Status IN ('Pending', 'Fulfilled', 'Cancelled')),
    CONSTRAINT chk_units CHECK (UnitsRequired > 0)
);

-- 7. Auto-Expiry View (Automatically marks blood older than 42 days as Expired)
CREATE VIEW ActiveBloodInventory AS
SELECT 
    BloodBagID, BankID, BloodGroup, CollectionDate,
    CASE 
        WHEN DATEDIFF(CURRENT_DATE, CollectionDate) > 42 THEN 'Expired'
        ELSE Status 
    END AS CurrentStatus
FROM BloodInventory;