import mysql.connector
from .database import connect_to_database


# ============================================================
# PATIENT MANAGEMENT
# ============================================================

def get_all_patients():
    """Lấy toàn bộ danh sách bệnh nhân để hiển thị lên Web"""
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Patients")
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
    return []


def add_patient(name, dob, gender, address, phone):
    """Adds a new patient record to the database."""
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            query = """INSERT INTO Patients (PatientName, DateOfBirth, Gender, Address, PhoneNumber)
                       VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query, (name, dob, gender, address, phone))
            conn.commit()
            print(f"Patient '{name}' added successfully. ID: {cursor.lastrowid}")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()


def search_patient(patient_id):
    """Retrieves patient information by ID."""
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM Patients WHERE PatientID = %s"
            cursor.execute(query, (patient_id,))
            result = cursor.fetchone()
            return result
        finally:
            cursor.close()
            conn.close()


def update_patient(patient_id, name=None, dob=None, gender=None, address=None, phone=None):
    """
    Updates one or more fields of an existing patient record.
    Only fields that are provided (not None) will be updated.
    """
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()

            # Dynamically build SET clause from provided fields only
            fields = []
            values = []
            if name:
                fields.append("PatientName = %s");    values.append(name)
            if dob:
                fields.append("DateOfBirth = %s");    values.append(dob)
            if gender:
                fields.append("Gender = %s");         values.append(gender)
            if address:
                fields.append("Address = %s");        values.append(address)
            if phone:
                fields.append("PhoneNumber = %s");    values.append(phone)

            if not fields:
                print("No fields to update.")
                return

            values.append(patient_id)
            query = f"UPDATE Patients SET {', '.join(fields)} WHERE PatientID = %s"
            cursor.execute(query, values)
            conn.commit()

            if cursor.rowcount:
                print(f"Patient ID {patient_id} updated successfully.")
            else:
                print(f"No patient found with ID {patient_id}.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()


def delete_patient(patient_id):
    """Deletes a patient record from the database."""
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            query = "DELETE FROM Patients WHERE PatientID = %s"
            cursor.execute(query, (patient_id,))
            conn.commit()
            if cursor.rowcount:
                print(f"Patient ID {patient_id} deleted successfully.")
            else:
                print(f"No patient found with ID {patient_id}.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()


# ============================================================
# DOCTOR MANAGEMENT
# ============================================================

def get_all_doctors():
    """Lấy danh sách bác sĩ"""
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            # Giả định bảng của bạn tên là Doctors
            cursor.execute("SELECT * FROM Doctors")
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
    return []

def add_doctor(name, specialty, department_id):
    """Adds a new doctor record to the database."""
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            query = "INSERT INTO Doctors (DoctorName, Specialty, DepartmentID) VALUES (%s, %s, %s)"
            cursor.execute(query, (name, specialty, department_id))
            conn.commit()
            print(f"Doctor '{name}' added successfully. ID: {cursor.lastrowid}")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()


def update_doctor(doctor_id, name=None, specialty=None, department_id=None):
    """
    Updates one or more fields of an existing doctor record.
    Only fields that are provided (not None) will be updated.
    """
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()

            fields = []
            values = []
            if name:
                fields.append("DoctorName = %s");    values.append(name)
            if specialty:
                fields.append("Specialty = %s");     values.append(specialty)
            if department_id:
                fields.append("DepartmentID = %s");  values.append(department_id)

            if not fields:
                print("No fields to update.")
                return

            values.append(doctor_id)
            query = f"UPDATE Doctors SET {', '.join(fields)} WHERE DoctorID = %s"
            cursor.execute(query, values)
            conn.commit()

            if cursor.rowcount:
                print(f"Doctor ID {doctor_id} updated successfully.")
            else:
                print(f"No doctor found with ID {doctor_id}.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()


def delete_doctor(doctor_id):
    """Deletes a doctor record from the database."""
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Doctors WHERE DoctorID = %s", (doctor_id,))
            conn.commit()
            if cursor.rowcount:
                print(f"Doctor ID {doctor_id} deleted successfully.")
            else:
                print(f"No doctor found with ID {doctor_id}.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()


# ============================================================
# APPOINTMENT MANAGEMENT
# ============================================================

def get_all_appointments():
    """Lấy danh sách lịch hẹn"""
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            # Lưu ý: Tên cột trong DB nên khớp với app.js (ví dụ: patientId, doctorId)
            # Nếu DB dùng patient_id, hãy dùng: SELECT id, patient_id AS patientId, ...
            cursor.execute("SELECT * FROM Appointments")
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
    return []

def schedule_appointment(doctor_id, patient_id, appt_date, appt_time):
    """
    Schedules a new appointment via the AddAppointment stored procedure.
    The PreventDoubleBooking trigger runs automatically inside the procedure.
    """
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.callproc('AddAppointment', (doctor_id, patient_id, appt_date, appt_time))
            conn.commit()
            print("Appointment scheduled successfully.")
        except mysql.connector.Error as err:
            raise Exception(str(err))
        finally:
            cursor.close()
            conn.close()


def cancel_appointment(appointment_id):
    """
    Cancels an appointment via the CancelAppointment stored procedure.
    The procedure prevents cancelling already-completed appointments.
    The AfterAppointmentUpdate trigger automatically logs the status change to AuditLog.
    """
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.callproc('CancelAppointment', (appointment_id,))
            conn.commit()
            # Fetch the message returned by the stored procedure
            for result in cursor.stored_results():
                row = result.fetchone()
                if row:
                    print(row[0])
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()


# ============================================================
# INVOICE MANAGEMENT
# ============================================================

def get_all_invoices():
    """Lấy danh sách hóa đơn"""
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Invoices")
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
    return []

def create_invoice(patient_id, amount):
    """
    Creates a new invoice with a direct INSERT.
    The AfterInvoiceInsert trigger automatically writes a record to AuditLog.
    """
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO Invoices (PatientID, InvoiceDate, TotalAmount, PaymentStatus)
                   VALUES (%s, CURDATE(), %s, 'Unpaid')""",
                (patient_id, amount)
            )
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error creating invoice: {err}")
        finally:
            cursor.close()
            conn.close()
    return None

def update_appointment(appointment_id, status):
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            # Kiểm tra status hiện tại
            cursor.execute("SELECT Status FROM Appointments WHERE AppointmentID = %s", (appointment_id,))
            row = cursor.fetchone()
            if row and row['Status'] == 'Completed':
                raise Exception("Cannot modify a completed appointment.")
            cursor.execute(
                "UPDATE Appointments SET Status = %s WHERE AppointmentID = %s",
                (status, appointment_id)
            )
            conn.commit()
        except mysql.connector.Error as err:
            raise Exception(str(err))
        finally:
            cursor.close()
            conn.close()


def update_invoice(invoice_id, amount=None, status=None):
    """Updates amount and/or payment status of an existing invoice."""
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            fields, values = [], []
            if amount is not None:
                fields.append("TotalAmount = %s"); values.append(amount)
            if status is not None:
                fields.append("PaymentStatus = %s"); values.append(status)
            if not fields:
                return
            values.append(invoice_id)
            cursor.execute(f"UPDATE Invoices SET {', '.join(fields)} WHERE InvoiceID = %s", values)
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()


def delete_invoice(invoice_id):
    """Deletes an invoice record from the database."""
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Invoices WHERE InvoiceID = %s", (invoice_id,))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()


def get_all_audit_logs():
    conn = connect_to_database()
    if conn:
        try:
            # Phải có dictionary=True
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM AuditLog") # Kiểm tra lại tên bảng trong MySQL
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
    return []

def add_audit_log(table_name, action, record_id, notes):
    """Ghi lại lịch sử thao tác vào bảng AuditLog trong MySQL"""
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            # Lưu ý: Tên cột phải khớp y hệt trong MySQL của bạn (TableName, Action, RecordID, Notes)
            sql = "INSERT INTO AuditLog (TableName, Action, RecordID, Notes) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (table_name, action, record_id, notes))
            conn.commit() # CỰC KỲ QUAN TRỌNG: Phải commit thì MySQL mới lưu[cite: 11]
        finally:
            cursor.close()
            conn.close()