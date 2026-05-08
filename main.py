from flask import Flask, render_template, jsonify, request
from database.operations import (
    get_all_patients, add_patient, update_patient, delete_patient,
    get_all_doctors, add_doctor, update_doctor, 
    get_all_appointments, schedule_appointment, cancel_appointment,
    get_all_invoices, create_invoice, get_all_audit_logs, add_audit_log
)

app = Flask(__name__)

# ─── 1. GIAO DIỆN CHÍNH ───
@app.route('/')
def index():
    return render_template('index.html')

# ─── 2. QUẢN LÝ BỆNH NHÂN (PATIENTS) ───
@app.route('/api/patients', methods=['GET'])
def api_get_patients():
    db_patients = get_all_patients()
    formatted = []
    for p in db_patients:
        formatted.append({
            "id": p["PatientID"],       # Map PatientID từ MySQL thành id cho JS
            "name": p["PatientName"],
            "dob": str(p["DateOfBirth"]), # Ép kiểu string để tránh lỗi JSON
            "gender": p["Gender"],
            "phone": p["PhoneNumber"],
            "address": p["Address"]
        })
    return jsonify(formatted)

@app.route('/api/patients', methods=['POST'])
def api_add_patient():
    data = request.json
    add_patient(data['name'], data['dob'], data['gender'], data['address'], data['phone'])
    return jsonify({"status": "success"})

@app.route('/api/patients/<int:id>', methods=['PUT'])
def api_update_patient(id):
    data = request.json
    update_patient(id, data['name'], data['dob'], data['gender'], data['address'], data['phone'])
    return jsonify({"status": "success"})

@app.route('/api/patients/<int:id>', methods=['DELETE'])
def api_delete_patient(id):
    delete_patient(id)
    return jsonify({"status": "success"})

# ─── 3. QUẢN LÝ BÁC SĨ (DOCTORS) ───
@app.route('/api/doctors', methods=['GET'])
def api_get_doctors():
    db_doctors = get_all_doctors()
    formatted = []
    for d in db_doctors:
        formatted.append({
            "id": d["DoctorID"],
            "name": d["DoctorName"],
            "specialty": d["Specialty"],
            "dept": d["DepartmentID"]
        })
    return jsonify(formatted)

@app.route('/api/doctors', methods=['POST'])
def api_add_doctor():
    data = request.json
    add_doctor(data['name'], data['specialty'], data['dept'])
    return jsonify({"status": "success"})

@app.route('/api/doctors/<int:id>', methods=['PUT'])
def api_update_doctor(id):
    data = request.json
    update_doctor(id, data['name'], data['specialty'], data['dept'])
    return jsonify({"status": "success"})

# ─── 4. QUẢN LÝ LỊCH HẸN (APPOINTMENTS) ───
@app.route('/api/doctors/<int:id>', methods=['DELETE'])
def api_delete_doctor(id):
    from database.operations import delete_doctor
    delete_doctor(id)
    return jsonify({"status": "success"})

@app.route('/api/appointments', methods=['GET'])
def api_get_appointments():
    db_appts = get_all_appointments()
    formatted = []
    for a in db_appts:
        formatted.append({
            "id": a["AppointmentID"],
            "patientId": a["PatientID"],
            "doctorId": a["DoctorID"],
            "date": str(a["AppointmentDate"]),
            "time": str(a["AppointmentTime"]),
            "status": a["Status"]
        })
    return jsonify(formatted)

@app.route('/api/appointments', methods=['POST'])
def api_schedule_appointment():
    data = request.json
    try:
        schedule_appointment(data['doctorId'], data['patientId'], data['date'], data['time'])
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 409

@app.route('/api/appointments/<int:id>', methods=['PUT'])
def api_update_appointment(id):
    data = request.json
    from database.operations import update_appointment
    update_appointment(id, data.get('status'))
    return jsonify({"status": "success"})

@app.route('/api/appointments/<int:id>', methods=['DELETE'])
def api_cancel_appointment(id):
    cancel_appointment(id)
    return jsonify({"status": "success"})

# ─── 5. QUẢN LÝ HÓA ĐƠN (INVOICES) ───
@app.route('/api/invoices', methods=['GET'])
def api_get_invoices():
    db_invoices = get_all_invoices()
    formatted = []
    for i in db_invoices:
        formatted.append({
            "id": i["InvoiceID"],
            "patientId": i["PatientID"],
            "date": str(i["InvoiceDate"]),
            "amount": float(i["TotalAmount"]),
            "status": i["PaymentStatus"]
        })
    return jsonify(formatted)

@app.route('/api/invoices', methods=['POST'])
def api_create_invoice():
    data = request.json
    try:
        result = create_invoice(data['patientId'], data['amount'])
        if result is None:
            return jsonify({"status": "error", "message": "Invoice creation failed"}), 500
        return jsonify({"status": "success", "invoiceId": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/invoices/<int:id>', methods=['PUT'])
def api_update_invoice(id):
    data = request.json
    from database.operations import update_invoice
    update_invoice(id, data.get('amount'), data.get('status'))
    return jsonify({"status": "success"})

@app.route('/api/invoices/<int:id>', methods=['DELETE'])
def api_delete_invoice(id):
    from database.operations import delete_invoice
    delete_invoice(id)
    return jsonify({"status": "success"})

@app.route('/api/audit', methods=['GET'])
def api_get_audit():
    db_logs = get_all_audit_logs()
    formatted = []
    
    for l in db_logs:
        formatted.append({
            "id": l.get("LogID") or 0,
            "table": l.get("TableName") or "Unknown",
            "action": l.get("Action") or "Unknown",
            "recordId": l.get("RecordID") or 0,
            "time": str(l.get("ChangedAt") or ""),
            "notes": l.get("Notes") or ""
        })
    return jsonify(formatted)

@app.route('/api/audit', methods=['POST'])
def api_add_audit():
    data = request.json 
    if data:
        add_audit_log(
            data.get('table'), 
            data.get('action'), 
            data.get('recordId'), 
            data.get('notes')
        )
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "No data received"}), 400

if __name__ == "__main__":
    app.run(debug=True)