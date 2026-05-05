-- SECTION 1: CREATE DATABASE

DROP DATABASE IF EXISTS HospitalManagement;
CREATE DATABASE HospitalManagement
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE HospitalManagement;


-- SECTION 2: CREATE TABLES

-- 2.1 Departments
CREATE TABLE Departments (
    DepartmentID INT PRIMARY KEY AUTO_INCREMENT,
    DepartmentName VARCHAR(100) NOT NULL UNIQUE
);

-- 2.2 Doctors
CREATE TABLE Doctors (
    DoctorID INT PRIMARY KEY AUTO_INCREMENT,
    DoctorName VARCHAR(100) NOT NULL,
    Specialty VARCHAR(100),
    DepartmentID INT,
    FOREIGN KEY (DepartmentID) REFERENCES Departments(DepartmentID)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

-- 2.3 Patients
CREATE TABLE Patients (
    PatientID INT PRIMARY KEY AUTO_INCREMENT,
    PatientName VARCHAR(100) NOT NULL,
    DateOfBirth DATE,
    Gender VARCHAR(10) CHECK (Gender IN ('Male', 'Female', 'Other')),
    Address VARCHAR(255),
    PhoneNumber VARCHAR(15)
);

-- 2.4 Appointments
CREATE TABLE Appointments (
    AppointmentID INT PRIMARY KEY AUTO_INCREMENT,
    DoctorID INT,
    PatientID INT,
    AppointmentDate DATE NOT NULL,
    AppointmentTime TIME NOT NULL,
    Status VARCHAR(20) DEFAULT 'Scheduled'
        CHECK (Status IN ('Scheduled', 'Completed', 'Cancelled')),
    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID)
        ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- 2.5 Invoices
CREATE TABLE Invoices (
    InvoiceID INT PRIMARY KEY AUTO_INCREMENT,
    PatientID INT,
    InvoiceDate DATE NOT NULL,
    TotalAmount DECIMAL(10, 2) NOT NULL CHECK (TotalAmount >= 0),
    PaymentStatus VARCHAR(20) DEFAULT 'Unpaid'
        CHECK (PaymentStatus IN ('Unpaid', 'Paid', 'Partially Paid')),
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- 2.6 Audit Log  (records key data-change events automatically via triggers)
CREATE TABLE AuditLog (
    LogID INT PRIMARY KEY AUTO_INCREMENT,
    TableName VARCHAR(50) NOT NULL,
    Action VARCHAR(20) NOT NULL,
    RecordID INT,
    ChangedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    Notes VARCHAR(255)
);


-- SECTION 3: SAMPLE DATA

-- 3.1 Departments (10 records)
INSERT INTO Departments (DepartmentName) VALUES
    ('Cardiology'),
    ('Pediatrics'),
    ('Neurology'),
    ('Orthopedics'),
    ('General Medicine'),
    ('Dermatology'),
    ('Oncology'),
    ('Radiology'),
    ('Emergency Medicine'),
    ('Ophthalmology');

-- 3.2 Doctors (10 records)
INSERT INTO Doctors (DoctorName, Specialty, DepartmentID) VALUES
    ('Dr. Robert Smith', 'Cardiologist', 1),
    ('Dr. Linda Johnson', 'Pediatrician', 2),
    ('Dr. Michael Wong', 'Neurologist', 3),
    ('Dr. Sarah Davis', 'Orthopedic Surgeon', 4),
    ('Dr. James Wilson', 'General Practitioner', 5),
    ('Dr. Emily Chen', 'Dermatologist', 6),
    ('Dr. Carlos Rivera', 'Oncologist', 7),
    ('Dr. Anna Mueller', 'Radiologist', 8),
    ('Dr. Kevin OBrien', 'Emergency Physician', 9),
    ('Dr. Priya Patel', 'Ophthalmologist', 10);

-- 3.3 Patients (10 records)
INSERT INTO Patients (PatientName, DateOfBirth, Gender, Address, PhoneNumber) VALUES
    ('Alice Brown', '1985-03-12', 'Female', '123 Maple St, NY', '555-0101'),
    ('Bob White', '1992-07-22', 'Male', '456 Oak Ave, CA', '555-0102'),
    ('Charlie Green', '1978-11-30', 'Male', '789 Pine Rd, TX', '555-0103'),
    ('Diana Prince', '2000-01-05', 'Female', '101 Cedar Ln, FL', '555-0104'),
    ('Edward Norton', '1965-05-18', 'Male', '202 Birch Blvd, WA', '555-0105'),
    ('Fiona Apple', '1990-09-25', 'Female', '303 Elm St, IL', '555-0106'),
    ('George Miller', '1975-12-08', 'Male', '404 Spruce Dr, OH', '555-0107'),
    ('Hannah Lee', '2003-04-17', 'Female', '505 Willow Way, GA', '555-0108'),
    ('Ivan Drago', '1988-06-30', 'Male', '606 Aspen Ct, CO', '555-0109'),
    ('Julia Roberts', '1995-02-14', 'Female', '707 Chestnut Ave, MA', '555-0110');

-- 3.4 Appointments (10 records)
INSERT INTO Appointments (DoctorID, PatientID, AppointmentDate, AppointmentTime, Status) VALUES
    (1, 1, '2024-06-01', '09:00:00', 'Completed'),
    (2, 2, '2024-06-01', '10:30:00', 'Completed'),
    (3, 3, '2024-06-02', '14:00:00', 'Completed'),
    (4, 4, '2024-06-03', '08:45:00', 'Completed'),
    (5, 5, '2024-06-03', '11:15:00', 'Completed'),
    (6, 6, '2024-06-04', '09:30:00', 'Scheduled'),
    (7, 7, '2024-06-04', '13:00:00', 'Scheduled'),
    (8, 8, '2024-06-05', '10:00:00', 'Scheduled'),
    (9, 9, '2024-06-05', '15:30:00', 'Cancelled'),
    (10, 10, '2024-06-06', '08:00:00', 'Scheduled');

-- 3.5 Invoices (10 records)
INSERT INTO Invoices (PatientID, InvoiceDate, TotalAmount, PaymentStatus) VALUES
    (1, '2024-06-01', 250.00, 'Paid'),
    (2, '2024-06-01', 120.50, 'Paid'),
    (3, '2024-06-02', 300.00, 'Paid'),
    (4, '2024-06-03', 450.75, 'Unpaid'),
    (5, '2024-06-03',  85.00, 'Paid'),
    (6, '2024-06-04', 175.00, 'Unpaid'),
    (7, '2024-06-04', 620.00, 'Partially Paid'),
    (8, '2024-06-05', 390.25, 'Unpaid'),
    (9, '2024-06-05',  55.00, 'Paid'),
    (10, '2024-06-06', 280.00, 'Unpaid');


-- SECTION 4: INDEXES

-- Speed up patient name searches
CREATE INDEX idx_patient_name
    ON Patients(PatientName);

-- Speed up appointment date range queries
CREATE INDEX idx_appointment_date
    ON Appointments(AppointmentDate);

-- Speed up appointment lookup by doctor
CREATE INDEX idx_appointment_doctor
    ON Appointments(DoctorID);

-- Composite index: doctor + date (common filter in scheduling queries)
CREATE INDEX idx_appt_doctor_date
    ON Appointments(DoctorID, AppointmentDate);

-- Speed up invoice lookup by patient
CREATE INDEX idx_invoice_patient
    ON Invoices(PatientID);

-- Speed up patient search by phone number
CREATE INDEX idx_patient_phone
    ON Patients(PhoneNumber);


-- SECTION 5: VIEWS

-- 5.1 Today's full appointment schedule
CREATE VIEW DailyAppointments AS
SELECT
    a.AppointmentID,
    p.PatientName,
    p.PhoneNumber,
    d.DoctorName,
    dept.DepartmentName,
    a.AppointmentDate,
    a.AppointmentTime,
    a.Status
FROM Appointments a
JOIN Patients p ON a.PatientID = p.PatientID
JOIN Doctors d ON a.DoctorID = d.DoctorID
JOIN Departments dept ON d.DepartmentID = dept.DepartmentID
WHERE a.AppointmentDate = CURDATE();

-- 5.2 Patient financial summary
CREATE VIEW PatientInvoiceSummary AS
SELECT
    p.PatientID,
    p.PatientName,
    COUNT(i.InvoiceID) AS TotalInvoices,
    COALESCE(SUM(i.TotalAmount), 0) AS TotalBilled,
    COALESCE(SUM(CASE WHEN i.PaymentStatus = 'Paid' THEN i.TotalAmount ELSE 0 END), 0) AS TotalPaid,
    COALESCE(SUM(CASE WHEN i.PaymentStatus != 'Paid' THEN i.TotalAmount ELSE 0 END), 0) AS TotalOutstanding
FROM Patients p
LEFT JOIN Invoices i ON p.PatientID = i.PatientID
GROUP BY p.PatientID, p.PatientName;

-- 5.3 Doctor workload summary
CREATE VIEW DoctorWorkloadSummary AS
SELECT
    d.DoctorID,
    d.DoctorName,
    d.Specialty,
    dept.DepartmentName,
    COUNT(a.AppointmentID) AS TotalAppointments,
    SUM(CASE WHEN a.Status = 'Completed' THEN 1 ELSE 0 END) AS Completed,
    SUM(CASE WHEN a.Status = 'Scheduled' THEN 1 ELSE 0 END) AS Upcoming,
    SUM(CASE WHEN a.Status = 'Cancelled' THEN 1 ELSE 0 END) AS Cancelled
FROM Doctors d
JOIN Departments dept ON d.DepartmentID = dept.DepartmentID
LEFT JOIN Appointments a ON d.DoctorID  = a.DoctorID
GROUP BY d.DoctorID, d.DoctorName, d.Specialty, dept.DepartmentName;

-- 5.4 Unpaid invoices report
CREATE VIEW UnpaidInvoices AS
SELECT
    i.InvoiceID,
    p.PatientName,
    p.PhoneNumber,
    i.InvoiceDate,
    i.TotalAmount,
    i.PaymentStatus
FROM Invoices i
JOIN Patients p ON i.PatientID = p.PatientID
WHERE i.PaymentStatus IN ('Unpaid', 'Partially Paid')
ORDER BY i.InvoiceDate;


-- SECTION 6: STORED PROCEDURES

-- 6.1 Add a new appointment
DELIMITER //
CREATE PROCEDURE AddAppointment(
    IN p_doctor_id  INT,
    IN p_patient_id INT,
    IN p_date DATE,
    IN p_time TIME
)
BEGIN
    -- PreventDoubleBooking trigger enforces no-overlap automatically
    INSERT INTO Appointments (DoctorID, PatientID, AppointmentDate, AppointmentTime)
    VALUES (p_doctor_id, p_patient_id, p_date, p_time);

    SELECT LAST_INSERT_ID() AS NewAppointmentID;
END //
DELIMITER ;

-- 6.2 Cancel an appointment
DELIMITER //
CREATE PROCEDURE CancelAppointment(
    IN p_appointment_id INT
)
BEGIN
    DECLARE v_status VARCHAR(20);

    SELECT Status INTO v_status
    FROM Appointments
    WHERE AppointmentID = p_appointment_id;

    IF v_status IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Error: Appointment not found.';
    ELSEIF v_status = 'Completed' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Error: Cannot cancel a completed appointment.';
    ELSE
        UPDATE Appointments
        SET Status = 'Cancelled'
        WHERE AppointmentID = p_appointment_id;

        SELECT 'Appointment cancelled successfully.' AS Message;
    END IF;
END //
DELIMITER ;

-- 6.3 Generate an invoice for a patient
DELIMITER //
CREATE PROCEDURE CreateInvoice(
    IN  p_patient_id INT,
    IN  p_amount DECIMAL(10,2),
    OUT p_invoice_id INT
)
BEGIN
    IF p_amount <= 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Error: Invoice amount must be greater than zero.';
    END IF;

    INSERT INTO Invoices (PatientID, InvoiceDate, TotalAmount, PaymentStatus)
    VALUES (p_patient_id, CURDATE(), p_amount, 'Unpaid');

    SET p_invoice_id = LAST_INSERT_ID();
END //
DELIMITER ;

-- 6.4 Get full appointment history for a patient
DELIMITER //
CREATE PROCEDURE GetPatientAppointments(
    IN p_patient_id INT
)
BEGIN
    SELECT
        a.AppointmentID,
        a.AppointmentDate,
        a.AppointmentTime,
        a.Status,
        d.DoctorName,
        dept.DepartmentName
    FROM Appointments  a
    JOIN Doctors d ON a.DoctorID = d.DoctorID
    JOIN Departments dept ON d.DepartmentID = dept.DepartmentID
    WHERE a.PatientID = p_patient_id
    ORDER BY a.AppointmentDate DESC, a.AppointmentTime DESC;
END //
DELIMITER ;

-- 6.5 Monthly revenue report
DELIMITER //
CREATE PROCEDURE MonthlyRevenueReport(
    IN p_year INT,
    IN p_month INT
)
BEGIN
    -- Detailed invoice list
    SELECT
        p.PatientName,
        i.InvoiceDate,
        i.TotalAmount,
        i.PaymentStatus
    FROM Invoices i
    JOIN Patients p ON i.PatientID = p.PatientID
    WHERE YEAR(i.InvoiceDate) = p_year
      AND MONTH(i.InvoiceDate) = p_month
    ORDER BY i.InvoiceDate;

    -- Aggregated summary
    SELECT
        COUNT(*) AS TotalInvoices,
        COALESCE(SUM(TotalAmount), 0) AS GrossRevenue,
        COALESCE(SUM(CASE WHEN PaymentStatus = 'Paid'  THEN TotalAmount ELSE 0 END), 0) AS CollectedRevenue,
        COALESCE(SUM(CASE WHEN PaymentStatus != 'Paid' THEN TotalAmount ELSE 0 END), 0) AS OutstandingRevenue
    FROM Invoices
    WHERE YEAR(InvoiceDate) = p_year
      AND MONTH(InvoiceDate) = p_month;
END //
DELIMITER ;


-- SECTION 7: USER-DEFINED FUNCTIONS

-- 7.1 Calculate total with 10% VAT
DELIMITER //
CREATE FUNCTION CalculateTotalWithTax(amount DECIMAL(10,2))
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    RETURN ROUND(amount * 1.10, 2);
END //
DELIMITER ;

-- 7.2 Calculate patient age from date of birth
DELIMITER //
CREATE FUNCTION GetPatientAge(p_dob DATE)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE v_age INT;
    SET v_age = TIMESTAMPDIFF(YEAR, p_dob, CURDATE());
    RETURN v_age;
END //
DELIMITER ;

-- 7.3 Get total appointment count for a doctor
DELIMITER //
CREATE FUNCTION GetDoctorAppointmentCount(p_doctor_id INT)
RETURNS INT
READS SQL DATA
BEGIN
    DECLARE v_count INT;
    SELECT COUNT(*) INTO v_count
    FROM Appointments
    WHERE DoctorID = p_doctor_id;
    RETURN v_count;
END //
DELIMITER ;

-- 7.4 Build a display label for a patient (Name + Age)
DELIMITER //
CREATE FUNCTION GetPatientLabel(p_patient_id INT)
RETURNS VARCHAR(150)
READS SQL DATA
BEGIN
    DECLARE v_label VARCHAR(150);
    SELECT CONCAT(PatientName, ' (Age: ', TIMESTAMPDIFF(YEAR, DateOfBirth, CURDATE()), ')')
    INTO v_label
    FROM Patients
    WHERE PatientID = p_patient_id;
    RETURN v_label;
END //
DELIMITER ;


-- SECTION 8: TRIGGERS

-- 8.1 Prevent future date of birth on INSERT
DELIMITER //
CREATE TRIGGER BeforePatientInsert
BEFORE INSERT ON Patients
FOR EACH ROW
BEGIN
    IF NEW.DateOfBirth > CURDATE() THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Error: Date of Birth cannot be in the future.';
    END IF;
END //
DELIMITER ;

-- 8.2 Prevent future date of birth on UPDATE
DELIMITER //
CREATE TRIGGER BeforePatientUpdate
BEFORE UPDATE ON Patients
FOR EACH ROW
BEGIN
    IF NEW.DateOfBirth > CURDATE() THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Error: Date of Birth cannot be in the future.';
    END IF;
END //
DELIMITER ;

-- 8.3 Prevent doctor double-booking (active appointments only)
DELIMITER //
CREATE TRIGGER PreventDoubleBooking
BEFORE INSERT ON Appointments
FOR EACH ROW
BEGIN
    DECLARE v_count INT;

    SELECT COUNT(*) INTO v_count
    FROM Appointments
    WHERE DoctorID = NEW.DoctorID
      AND AppointmentDate = NEW.AppointmentDate
      AND AppointmentTime = NEW.AppointmentTime
      AND Status != 'Cancelled';

    IF v_count > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Error: This doctor already has an active appointment at this time.';
    END IF;
END //
DELIMITER ;

-- 8.4 After invoice insert
DELIMITER //
CREATE TRIGGER AfterInvoiceInsert
AFTER INSERT ON Invoices
FOR EACH ROW
BEGIN
    INSERT INTO AuditLog (TableName, Action, RecordID, Notes)
    VALUES ('Invoices', 'INSERT', NEW.InvoiceID,
            CONCAT('Invoice created for PatientID ', NEW.PatientID,
                   ' | Amount: ', NEW.TotalAmount));
END //
DELIMITER ;

-- 8.5 Log every appointment status change
DELIMITER //
CREATE TRIGGER AfterAppointmentUpdate
AFTER UPDATE ON Appointments
FOR EACH ROW
BEGIN
    IF OLD.Status != NEW.Status THEN
        INSERT INTO AuditLog (TableName, Action, RecordID, Notes)
        VALUES ('Appointments', 'UPDATE', NEW.AppointmentID,
                CONCAT('Status changed: "', OLD.Status, '" -> "', NEW.Status, '"'));
    END IF;
END //
DELIMITER ;


-- SECTION 9: SECURITY — USER ROLES & PERMISSIONS

-- 9.1 Admin — full access to all tables and operations
CREATE USER IF NOT EXISTS 'admin_hospital'@'localhost' IDENTIFIED BY 'AdminPass@123';
GRANT ALL PRIVILEGES ON HospitalManagement.* TO 'admin_hospital'@'localhost';

-- 9.2 Doctor — view patients, manage appointments, view daily schedule
CREATE USER IF NOT EXISTS 'doctor_user'@'localhost' IDENTIFIED BY 'DoctorPass@456';
GRANT SELECT ON HospitalManagement.Patients TO 'doctor_user'@'localhost';
GRANT SELECT, INSERT, UPDATE  ON HospitalManagement.Appointments TO 'doctor_user'@'localhost';
GRANT SELECT ON HospitalManagement.DailyAppointments TO 'doctor_user'@'localhost';
GRANT SELECT ON HospitalManagement.DoctorWorkloadSummary TO 'doctor_user'@'localhost';

-- 9.3 Receptionist — register patients and manage appointments
CREATE USER IF NOT EXISTS 'receptionist_user'@'localhost' IDENTIFIED BY 'ReceptionPass@789';
GRANT SELECT, INSERT, UPDATE  ON HospitalManagement.Patients TO 'receptionist_user'@'localhost';
GRANT SELECT, INSERT, UPDATE  ON HospitalManagement.Appointments TO 'receptionist_user'@'localhost';
GRANT SELECT ON HospitalManagement.Doctors TO 'receptionist_user'@'localhost';
GRANT SELECT ON HospitalManagement.Departments TO 'receptionist_user'@'localhost';
GRANT SELECT ON HospitalManagement.DailyAppointments TO 'receptionist_user'@'localhost';

-- 9.4 Billing staff — manage invoices, no access to clinical data
CREATE USER IF NOT EXISTS 'billing_user'@'localhost' IDENTIFIED BY 'BillingPass@321';
GRANT SELECT, INSERT, UPDATE  ON HospitalManagement.Invoices TO 'billing_user'@'localhost';
GRANT SELECT ON HospitalManagement.Patients TO 'billing_user'@'localhost';
GRANT SELECT ON HospitalManagement.PatientInvoiceSummary TO 'billing_user'@'localhost';
GRANT SELECT ON HospitalManagement.UnpaidInvoices TO 'billing_user'@'localhost';

FLUSH PRIVILEGES;