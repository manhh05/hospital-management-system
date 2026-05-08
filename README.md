# 🏥 Hospital Management System

Hệ thống quản lý bệnh viện tích hợp, kết hợp cơ sở dữ liệu MySQL với ứng dụng web Flask, cung cấp giao diện hiện đại để quản lý toàn bộ hoạt động của cơ sở y tế.

---

## 📋 Mục lục

- [Tổng quan](#tổng-quan)
- [Tính năng](#tính-năng)
- [Kiến trúc hệ thống](#kiến-trúc-hệ-thống)
- [Cơ sở dữ liệu](#cơ-sở-dữ-liệu)
- [Cài đặt](#cài-đặt)
- [Hướng dẫn sử dụng](#hướng-dẫn-sử-dụng)
- [API Endpoints](#api-endpoints)
- [Bảo mật & Phân quyền](#bảo-mật--phân-quyền)
- [Cấu trúc thư mục](#cấu-trúc-thư-mục)

---

## Tổng quan

Hospital Management System (HMS) là giải pháp số hóa nhằm hiện đại hóa công tác quản lý hành chính và lâm sàng của cơ sở y tế. Hệ thống thay thế việc ghi chép thủ công bằng một framework tự động, hiệu quả, có khả năng xử lý dữ liệu y tế phức tạp.

**Công nghệ sử dụng:**

| Thành phần | Công nghệ |
|---|---|
| Backend | Python 3, Flask |
| Database | MySQL (mysql-connector-python) |
| Frontend | HTML, CSS, Vanilla JavaScript |
| Báo cáo | MySQL Views + Stored Procedures |

---

## Tính năng

### Quản lý nghiệp vụ

- **Bệnh nhân** — Thêm, sửa, xóa, tra cứu hồ sơ bệnh nhân (tên, ngày sinh, giới tính, địa chỉ, số điện thoại)
- **Bác sĩ** — Quản lý danh sách bác sĩ theo chuyên khoa và khoa phòng
- **Lịch hẹn** — Đặt lịch, cập nhật trạng thái (Scheduled / Completed / Cancelled), hủy lịch; tự động ngăn chặn đặt trùng lịch
- **Hóa đơn** — Tạo và quản lý hóa đơn bệnh nhân (Unpaid / Paid / Partially Paid)
- **Nhật ký kiểm toán** — Ghi log tự động mọi thay đổi quan trọng qua trigger

### Báo cáo & Thống kê

- Lịch hẹn trong ngày (Daily Appointments Report)
- Tóm tắt tài chính theo bệnh nhân (Financial Summary)
- Doanh thu theo tháng (Monthly Revenue Report)
- Thống kê lượt khám theo khoa (Patient Visits by Department)
- Xem nhật ký kiểm toán gần nhất

### Dashboard

Giao diện web hiển thị tổng quan: tổng số bệnh nhân, bác sĩ, lịch hẹn hôm nay, và doanh thu.

---

## Kiến trúc hệ thống

```
hospital_management/
├── main.py                  # Flask app — định nghĩa toàn bộ API routes
├── database/
│   ├── database.py          # Kết nối MySQL
│   ├── operations.py        # CRUD operations cho tất cả bảng
│   └── reports.py           # Truy vấn báo cáo, gọi Stored Procedures
├── static/
│   ├── css/style.css        # Giao diện
│   ├── js/app.js            # Logic frontend, gọi API
│   └── icons/               # SVG icons
├── templates/
│   └── index.html           # Giao diện SPA duy nhất
└── Hospital_Management_SQL.sql  # Script khởi tạo toàn bộ database
```

**Luồng dữ liệu:**

```
Trình duyệt (HTML/JS)
    ↕ fetch() API calls
Flask REST API (main.py)
    ↕ mysql-connector-python
MySQL Database (HospitalManagement)
```

---

## Cơ sở dữ liệu

### Các bảng chính

| Bảng | Mô tả |
|---|---|
| `Departments` | Danh sách khoa phòng (10 khoa mặc định) |
| `Doctors` | Thông tin bác sĩ, liên kết khoa |
| `Patients` | Hồ sơ bệnh nhân |
| `Appointments` | Lịch hẹn khám |
| `Invoices` | Hóa đơn thanh toán |
| `AuditLog` | Nhật ký thay đổi dữ liệu (tự động qua trigger) |

### Đối tượng nâng cao

**Indexes** — Tăng tốc độ truy vấn:
- `idx_patient_name`, `idx_appointment_date`, `idx_appointment_doctor`, `idx_appt_doctor_date`, `idx_invoice_patient`, `idx_patient_phone`

**Views** — Truy vấn tổng hợp:
- `DailyAppointments` — Lịch hẹn trong ngày kèm thông tin bác sĩ/bệnh nhân/khoa
- `PatientInvoiceSummary` — Tổng hóa đơn, số tiền đã trả, còn nợ theo bệnh nhân
- `DoctorWorkloadSummary` — Khối lượng công việc của từng bác sĩ
- `UnpaidInvoices` — Danh sách hóa đơn chưa thanh toán

**Stored Procedures:**
- `AddAppointment` — Đặt lịch hẹn (có kiểm tra trùng)
- `CancelAppointment` — Hủy lịch hẹn
- `CreateInvoice` — Tạo hóa đơn mới
- `GetPatientAppointments` — Lịch sử khám của bệnh nhân
- `MonthlyRevenueReport` — Báo cáo doanh thu tháng

**Functions:**
- `CalculateTotalWithTax(amount)` — Tính tổng tiền có thuế
- `GetPatientAge(dob)` — Tính tuổi bệnh nhân
- `GetDoctorAppointmentCount(doctor_id)` — Số lịch hẹn của bác sĩ
- `GetPatientLabel(patient_id)` — Nhãn định danh bệnh nhân

**Triggers:**
- `BeforePatientInsert` / `BeforePatientUpdate` — Validate dữ liệu đầu vào
- `PreventDoubleBooking` — Ngăn bác sĩ bị đặt lịch trùng giờ
- `AfterInvoiceInsert` — Ghi log khi tạo hóa đơn
- `AfterAppointmentUpdate` — Ghi log khi cập nhật trạng thái lịch hẹn

---

## Cài đặt

### Yêu cầu

- Python 3.8+
- MySQL Server 8.0+
- pip

### Các bước cài đặt

**1. Clone hoặc giải nén project**

```bash
cd hospital_management
```

**2. Cài đặt thư viện Python**

```bash
pip install flask mysql-connector-python
```

**3. Khởi tạo database**

Chạy toàn bộ script SQL trong MySQL Workbench hoặc terminal:

```bash
mysql -u root -p < Hospital_Management_SQL.sql
```

Script sẽ tự động:
- Tạo database `HospitalManagement`
- Tạo tất cả bảng, indexes, views, stored procedures, functions, triggers
- Thêm dữ liệu mẫu (10 khoa, 10 bác sĩ, bệnh nhân, lịch hẹn, hóa đơn)
- Tạo các tài khoản người dùng với phân quyền phù hợp

**4. Chạy ứng dụng**

```bash
python main.py
```

Mở trình duyệt và truy cập: `http://127.0.0.1:5000`

---

## Hướng dẫn sử dụng

Sau khi khởi động, giao diện web có các tab chính:

- **Dashboard** — Tổng quan số liệu hệ thống
- **Patients** — Quản lý hồ sơ bệnh nhân
- **Doctors** — Quản lý danh sách bác sĩ
- **Appointments** — Đặt và quản lý lịch hẹn
- **Invoices** — Quản lý hóa đơn thanh toán
- **Audit Log** — Xem nhật ký thay đổi dữ liệu

---

## API Endpoints

| Method | Endpoint | Chức năng |
|---|---|---|
| GET | `/api/patients` | Lấy danh sách bệnh nhân |
| POST | `/api/patients` | Thêm bệnh nhân mới |
| PUT | `/api/patients/<id>` | Cập nhật thông tin bệnh nhân |
| DELETE | `/api/patients/<id>` | Xóa bệnh nhân |
| GET | `/api/doctors` | Lấy danh sách bác sĩ |
| POST | `/api/doctors` | Thêm bác sĩ mới |
| PUT | `/api/doctors/<id>` | Cập nhật thông tin bác sĩ |
| DELETE | `/api/doctors/<id>` | Xóa bác sĩ |
| GET | `/api/appointments` | Lấy danh sách lịch hẹn |
| POST | `/api/appointments` | Đặt lịch hẹn mới |
| PUT | `/api/appointments/<id>` | Cập nhật trạng thái lịch hẹn |
| DELETE | `/api/appointments/<id>` | Hủy lịch hẹn |
| GET | `/api/invoices` | Lấy danh sách hóa đơn |
| POST | `/api/invoices` | Tạo hóa đơn mới |
| PUT | `/api/invoices/<id>` | Cập nhật hóa đơn |
| DELETE | `/api/invoices/<id>` | Xóa hóa đơn |
| GET | `/api/audit` | Lấy nhật ký kiểm toán |
| POST | `/api/audit` | Ghi log thủ công |

---

## Bảo mật & Phân quyền

Hệ thống sử dụng 4 tài khoản MySQL với phân quyền theo vai trò:

| Tài khoản | Vai trò | Quyền hạn |
|---|---|---|
| `admin_hospital` | Quản trị viên | Toàn quyền trên database |
| `doctor_user` | Bác sĩ | Xem bệnh nhân, xem/thêm/sửa lịch hẹn |
| `receptionist_user` | Lễ tân | Quản lý bệnh nhân, lịch hẹn; xem bác sĩ và khoa |
| `billing_user` | Kế toán | Quản lý hóa đơn, xem thông tin bệnh nhân |

---

## Khoa phòng mặc định

Hệ thống được khởi tạo sẵn với 10 khoa: Cardiology, Pediatrics, Neurology, Orthopedics, General Medicine, Dermatology, Oncology, Radiology, Emergency Medicine, Ophthalmology.