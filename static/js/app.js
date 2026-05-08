// ============================================================
//  HOSPITAL MANAGEMENT SYSTEM — Application Logic
//  File: app.js
// ============================================================

// ══ DATA STORE ══

const departments = [
  'Cardiology', 'Pediatrics', 'Neurology', 'Orthopedics', 'General Medicine',
  'Dermatology', 'Oncology', 'Radiology', 'Emergency Medicine', 'Ophthalmology'
];

let patients = [];
let doctors = [];
let appointments = [];
let invoices = [];
let auditLog = [];

let nextPatientId     = 11;
let nextDoctorId      = 11;
let nextAppointmentId = 11;
let nextInvoiceId     = 11;
let nextAuditId       = 6;

// ══ FETCH FUNCTIONS (KẾT NỐI DATABASE) ══

// Hàm chung để tải toàn bộ dữ liệu khi mở web
async function loadAllData() {
  await Promise.all([
    fetchPatients(),
    fetchDoctors(),
    fetchAppointments(),
    fetchInvoices(),
    fetchAuditLog()
  ]);
  renderDashboard(); // Sau khi có đủ data thì mới vẽ Dashboard
}

async function fetchPatients() {
  try {
    const res = await fetch('/api/patients');
    patients = await res.json();
    renderPatients();
  } catch (err) { console.error("Lỗi lấy dữ liệu Patients:", err); }
}

async function fetchDoctors() {
  try {
    const res = await fetch('/api/doctors');
    doctors = await res.json();
    renderDoctors();
  } catch (err) { console.error("Lỗi lấy dữ liệu Doctors:", err); }
}

async function fetchAppointments() {
  try {
    const res = await fetch('/api/appointments');
    appointments = await res.json();
    renderAppointments();
  } catch (err) { console.error("Lỗi lấy dữ liệu Appointments:", err); }
}

async function fetchInvoices() {
  try {
    const res = await fetch('/api/invoices');
    invoices = await res.json();
    renderInvoices();
  } catch (err) { console.error("Lỗi lấy dữ liệu Invoices:", err); }
}

async function fetchAuditLog() {
  try {
    const res = await fetch('/api/audit');
    if (!res.ok) throw new Error('Không thể kết nối API Audit');
    
    auditLog = await res.json();
    renderAudit();
  } catch (err) { 
    console.error("Lỗi lấy dữ liệu Audit Log:", err); 
  }
}

// ══ HELPERS ══

const getPatient = id => patients.find(p => p.id === id);
const getDoctor  = id => doctors.find(d => d.id === id);

const calcAge = dob => {
  const b = new Date(dob), n = new Date();
  let a = n.getFullYear() - b.getFullYear();
  if (n < new Date(n.getFullYear(), b.getMonth(), b.getDate())) a--;
  return a;
};

const fmtAmount = v => '$' + parseFloat(v).toFixed(2);
const withTax   = v => fmtAmount(parseFloat(v) * 1.10);

async function addAudit(tbl, action, rid, notes) {
  const logData = {
    table: tbl,
    action: action,
    recordId: rid,
    notes: notes
  };

  try {
    // Gửi log về Backend để lưu vào MySQL
    await fetch('/api/audit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(logData)
    });
    
    // Sau khi lưu thành công vào DB, load lại toàn bộ log để đảm bảo đồng bộ
    fetchAuditLog();
  } catch (err) {
    console.error("Lỗi không thể lưu Audit Log vào Database:", err);
  }
}

function statusBadge(s) {
  const map = { Completed: 'green', Scheduled: 'blue', Cancelled: 'red', Paid: 'green', Unpaid: 'red', 'Partially Paid': 'orange' };
  return `<span class="badge badge-${map[s] || 'gray'}">${s}</span>`;
}

function genderBadge(g) {
  return g === 'Female'
    ? `<span class="badge badge-orange">${g}</span>`
    : `<span class="badge badge-blue">${g}</span>`;
}

// ══ NAVIGATION ══

const pageTitles = {
  dashboard:    'Dashboard',
  patients:     'Patient Records',
  doctors:      'Medical Staff',
  appointments: 'Appointments',
  invoices:     'Invoices & Billing',
  audit:        'Audit Log'
};

function navigate(page) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('page-' + page).classList.add('active');
  document.querySelector(`.nav-item[onclick="navigate('${page}')"]`).classList.add('active');
  document.getElementById('topbar-title').textContent = pageTitles[page];

  if (page === 'dashboard')    renderDashboard();
  if (page === 'patients')     renderPatients();
  if (page === 'doctors')      renderDoctors();
  if (page === 'appointments') renderAppointments();
  if (page === 'invoices')     renderInvoices();
  if (page === 'audit')        renderAudit();
}

// ══ TOAST ══

function toast(msg, type = 'success') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = `toast ${type} show`;
  setTimeout(() => t.classList.remove('show'), 3000);
}

// ══ MODAL OPEN / CLOSE ══

function openModal(type, data = null) {
  if (type === 'patient') {
    document.getElementById('patient-modal-title').textContent = data ? 'Edit Patient' : 'Add Patient';
    document.getElementById('patient-id').value      = data ? data.id      : '';
    document.getElementById('patient-name').value    = data ? data.name    : '';
    document.getElementById('patient-dob').value     = data ? data.dob     : '';
    document.getElementById('patient-gender').value  = data ? data.gender  : 'Male';
    document.getElementById('patient-phone').value   = data ? data.phone   : '';
    document.getElementById('patient-address').value = data ? data.address : '';
  }

  if (type === 'doctor') {
    const sel = document.getElementById('doctor-dept');
    sel.innerHTML = departments.map(d => `<option>${d}</option>`).join('');
    document.getElementById('doctor-modal-title').textContent = data ? 'Edit Doctor' : 'Add Doctor';
    document.getElementById('doctor-id').value        = data ? data.id        : '';
    document.getElementById('doctor-name').value      = data ? data.name      : '';
    document.getElementById('doctor-specialty').value = data ? data.specialty : '';
    if (data) sel.value = data.dept;
  }

  if (type === 'appointment') {
    // Chặn edit nếu appointment đã Completed
    if (data && data.status === 'Completed') {
      toast('This appointment is completed and cannot be edited.', 'error');
      return;
    }
    document.getElementById('appt-patient').innerHTML = patients.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
    document.getElementById('appt-doctor').innerHTML  = doctors.map(d  => `<option value="${d.id}">${d.name}</option>`).join('');
    document.getElementById('appt-modal-title').textContent = data ? 'Edit Appointment' : 'New Appointment';
    document.getElementById('appt-id').value     = data ? data.id     : '';
    document.getElementById('appt-date').value   = data ? data.date   : '';
    document.getElementById('appt-time').value   = data ? data.time   : '';
    document.getElementById('appt-status').value = data ? data.status : 'Scheduled';
    if (data) {
      document.getElementById('appt-patient').value = data.patientId;
      document.getElementById('appt-doctor').value  = data.doctorId;
    }
  }

  if (type === 'invoice') {
    document.getElementById('inv-patient').innerHTML = patients.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
    document.getElementById('inv-modal-title').textContent = data ? 'Edit Invoice' : 'New Invoice';
    document.getElementById('inv-id').value     = data ? data.id     : '';
    document.getElementById('inv-date').value   = data ? data.date   : '';
    document.getElementById('inv-amount').value = data ? data.amount : '';
    document.getElementById('inv-status').value = data ? data.status : 'Unpaid';
    if (data) document.getElementById('inv-patient').value = data.patientId;
  }

  document.getElementById('modal-' + type).classList.add('open');
}

function closeModal(type) {
  document.getElementById('modal-' + type).classList.remove('open');
}

// ══ SAVE HANDLERS ══

function savePatient() {
  const name = document.getElementById('patient-name').value.trim();
  const dob  = document.getElementById('patient-dob').value;

  if (!name || !dob) { toast('Name and Date of Birth are required.', 'error'); return; }
  if (new Date(dob) > new Date()) { toast('Date of Birth cannot be in the future.', 'error'); return; }

  const id  = document.getElementById('patient-id').value;
  const obj = {
    name,
    dob,
    gender:  document.getElementById('patient-gender').value,
    phone:   document.getElementById('patient-phone').value,
    address: document.getElementById('patient-address').value,
  };

  if (id) {
    fetch(`/api/patients/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(obj)
    }).then(() => {
      addAudit('Patients', 'UPDATE', +id, `Patient "${name}" updated`);
      toast('Patient updated successfully.');
      fetchPatients();
      closeModal('patient');
    });
  } else {
    fetch('/api/patients', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(obj)
    }).then(() => {
      addAudit('Patients', 'INSERT', 0, `New patient "${name}" added`);
      toast('Patient added successfully.');
      fetchPatients();
      closeModal('patient');
    });
  }
}

function saveDoctor() {
  const name = document.getElementById('doctor-name').value.trim();
  if (!name) { toast('Doctor name is required.', 'error'); return; }

  const id  = document.getElementById('doctor-id').value;
  const obj = {
    name,
    specialty: document.getElementById('doctor-specialty').value,
    dept:      document.getElementById('doctor-dept').value,
  };

  if (id) {
    fetch(`/api/doctors/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(obj)
    }).then(() => {
      addAudit('Doctors', 'UPDATE', +id, `Doctor "${name}" updated`);
      toast('Doctor updated successfully.');
      fetchDoctors();
      closeModal('doctor');
    });
  } else {
    fetch('/api/doctors', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(obj)
    }).then(() => {
      addAudit('Doctors', 'INSERT', 0, `New doctor "${name}" added`);
      toast('Doctor added successfully.');
      fetchDoctors();
      closeModal('doctor');
    });
  }
}

function saveAppointment() {
  const pid    = +document.getElementById('appt-patient').value;
  const did    = +document.getElementById('appt-doctor').value;
  const date   = document.getElementById('appt-date').value;
  const time   = document.getElementById('appt-time').value;
  const status = document.getElementById('appt-status').value;
  const id     = document.getElementById('appt-id').value;

  if (!date || !time) { toast('Date and time are required.', 'error'); return; }

  // Confirm trước khi mark Completed (không thể hoàn tác)
  if (status === 'Completed') {
    if (!confirm('Are you sure you want to mark this appointment as Completed? This action cannot be undone.')) return;
  }

  // Double-booking check (mirrors PreventDoubleBooking trigger)
  const conflict = appointments.find(a =>
    a.doctorId === did &&
    a.date     === date &&
    a.time     === time &&
    a.status   !== 'Cancelled' &&
    a.id       != +id
  );
  if (conflict) { toast('This doctor already has an active appointment at this time!', 'error'); return; }

  const obj = { patientId: pid, doctorId: did, date, time, status };

  if (id) {
    fetch(`/api/appointments/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(obj)
    }).then(() => {
      if (obj.status !== status) {
        addAudit('Appointments', 'UPDATE', +id, `Status changed: "${status}"`);
      }
      toast('Appointment updated successfully.');
      fetchAppointments();
      closeModal('appointment');
    });
  } else {
    fetch('/api/appointments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(obj)
    }).then(() => {
      addAudit('Appointments', 'INSERT', 0, `New appointment for PatientID ${pid} with DoctorID ${did}`);
      toast('Appointment booked successfully.');
      fetchAppointments();
      closeModal('appointment');
    });
  }
}

function saveInvoice() {
  const pid    = +document.getElementById('inv-patient').value;
  let   date   = document.getElementById('inv-date').value;
  const amount = parseFloat(document.getElementById('inv-amount').value);
  const status = document.getElementById('inv-status').value;
  const id     = document.getElementById('inv-id').value;

  if (!date) date = new Date().toISOString().split('T')[0];

  if (isNaN(amount) || amount <= 0) { toast('Valid amount is required.', 'error'); return; }

  const obj = { patientId: pid, date, amount, status };

  if (id) {
    fetch(`/api/invoices/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(obj)
    }).then(() => {
      addAudit('Invoices', 'UPDATE', +id, `Invoice updated for PatientID ${pid} | Amount: ${amount}`);
      toast('Invoice updated successfully.');
      fetchInvoices();
      closeModal('invoice');
    });
  } else {
    fetch('/api/invoices', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(obj)
    }).then(res => res.json()).then(data => {
      if (data.status === 'error') { toast(data.message || 'Failed to create invoice.', 'error'); return; }
      addAudit('Invoices', 'INSERT', 0, `Invoice created for PatientID ${pid} | Amount: ${amount}`);
      toast('Invoice created successfully.');
      fetchInvoices();
      closeModal('invoice');
    }).catch(() => toast('Network error. Please try again.', 'error'));
  }
}

// ══ DELETE HANDLERS ══

function deletePatient(id) {
  if (!confirm('Delete this patient?')) return;
  fetch(`/api/patients/${id}`, { method: 'DELETE' }).then(() => {
    addAudit('Patients', 'DELETE', id, 'Patient record removed');
    fetchPatients();
    toast('Patient deleted.');
  });
}

function deleteDoctor(id) {
  if (!confirm('Delete this doctor?')) return;
  fetch(`/api/doctors/${id}`, { method: 'DELETE' }).then(() => {
    addAudit('Doctors', 'DELETE', id, 'Doctor record removed');
    fetchDoctors();
    toast('Doctor deleted.');
  });
}

function deleteAppointment(id) {
  if (!confirm('Cancel this appointment?')) return;
  fetch(`/api/appointments/${id}`, { method: 'DELETE' }).then(() => {
    addAudit('Appointments', 'DELETE', id, 'Appointment removed');
    fetchAppointments();
    toast('Appointment removed.');
  });
}

function deleteInvoice(id) {
  if (!confirm('Delete this invoice?')) return;
  fetch(`/api/invoices/${id}`, { method: 'DELETE' }).then(() => {
    addAudit('Invoices', 'DELETE', id, 'Invoice removed');
    fetchInvoices();
    toast('Invoice deleted.');
  });
}

// ══ RENDER FUNCTIONS ══

function renderPatients() {
  const q        = (document.getElementById('search-patients')?.value || '').toLowerCase();
  const filtered = patients.filter(p => p.name.toLowerCase().includes(q) || p.phone.includes(q));

  document.getElementById('patients-body').innerHTML = filtered.length
    ? filtered.map(p => `
        <tr>
          <td><span style="color:var(--muted);font-size:12px">#${p.id}</span></td>
          <td>
            <strong>${p.name}</strong>
            <div style="font-size:11px;color:var(--muted)">Age ${calcAge(p.dob)}</div>
          </td>
          <td>${p.dob}</td>
          <td>${genderBadge(p.gender)}</td>
          <td>${p.phone}</td>
          <td style="max-width:160px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${p.address}</td>
          <td>
            <div class="action-btns">
              <button class="icon-btn edit" onclick='openModal("patient",${JSON.stringify(p)})' title="Edit">✏️</button>
              <button class="icon-btn del"  onclick="deletePatient(${p.id})" title="Delete">🗑️</button>
            </div>
          </td>
        </tr>`).join('')
    : `<tr><td colspan="7"><div class="empty"><div class="empty-icon">👤</div>No patients found</div></td></tr>`;
}

function renderDoctors() {
  const q        = (document.getElementById('search-doctors')?.value || '').toLowerCase();
  const filtered = doctors.filter(d =>
    d.name.toLowerCase().includes(q) ||
    d.specialty.toLowerCase().includes(q) ||
    d.dept.toLowerCase().includes(q)
  );

  document.getElementById('doctors-body').innerHTML = filtered.length
    ? filtered.map(d => {
        const cnt = appointments.filter(a => a.doctorId === d.id).length;
        return `
          <tr>
            <td><span style="color:var(--muted);font-size:12px">#${d.id}</span></td>
            <td><strong>${d.name}</strong></td>
            <td>${d.specialty}</td>
            <td><span class="badge badge-blue">${d.dept}</span></td>
            <td><span class="badge badge-gray">${cnt} appts</span></td>
            <td>
              <div class="action-btns">
                <button class="icon-btn edit" onclick='openModal("doctor",${JSON.stringify(d)})' title="Edit">✏️</button>
                <button class="icon-btn del"  onclick="deleteDoctor(${d.id})" title="Delete">🗑️</button>
              </div>
            </td>
          </tr>`;
      }).join('')
    : `<tr><td colspan="6"><div class="empty"><div class="empty-icon">🩺</div>No doctors found</div></td></tr>`;
}

function renderAppointments() {
  const q        = (document.getElementById('search-appointments')?.value || '').toLowerCase();
  const filtered = appointments
    .filter(a => {
      const p = getPatient(a.patientId), d = getDoctor(a.doctorId);
      return (p?.name || '').toLowerCase().includes(q) ||
             (d?.name || '').toLowerCase().includes(q) ||
             a.status.toLowerCase().includes(q);
    })
    .sort((a, b) => a.date < b.date ? 1 : -1);

  document.getElementById('appointments-body').innerHTML = filtered.length
    ? filtered.map(a => {
        const p = getPatient(a.patientId), d = getDoctor(a.doctorId);
        return `
          <tr>
            <td><span style="color:var(--muted);font-size:12px">#${a.id}</span></td>
            <td>${p?.name || '—'}</td>
            <td>${d?.name || '—'}</td>
            <td><span class="badge badge-blue" style="font-size:10px">${d?.dept || '—'}</span></td>
            <td>${a.date}</td>
            <td>${a.time}</td>
            <td>${statusBadge(a.status)}</td>
            <td>
              <div class="action-btns">
                <button class="icon-btn edit" onclick='openModal("appointment",${JSON.stringify(a)})' title="Edit">✏️</button>
                <button class="icon-btn del"  onclick="deleteAppointment(${a.id})" title="Delete">🗑️</button>
              </div>
            </td>
          </tr>`;
      }).join('')
    : `<tr><td colspan="8"><div class="empty"><div class="empty-icon">📅</div>No appointments found</div></td></tr>`;
}

function renderInvoices() {
  const q        = (document.getElementById('search-invoices')?.value || '').toLowerCase();
  const filtered = invoices
    .filter(i => {
      const p = getPatient(i.patientId);
      return (p?.name || '').toLowerCase().includes(q) || i.status.toLowerCase().includes(q);
    })
    .sort((a, b) => a.date < b.date ? 1 : -1);

  document.getElementById('invoices-body').innerHTML = filtered.length
    ? filtered.map(i => {
        const p = getPatient(i.patientId);
        return `
          <tr>
            <td><span style="color:var(--muted);font-size:12px">#${i.id}</span></td>
            <td>${p?.name || '—'}</td>
            <td>${i.date}</td>
            <td><strong>${fmtAmount(i.amount)}</strong></td>
            <td style="color:var(--teal);font-weight:500">${withTax(i.amount)}</td>
            <td>${statusBadge(i.status)}</td>
            <td>
              <div class="action-btns">
                <button class="icon-btn edit" onclick='openModal("invoice",${JSON.stringify(i)})' title="Edit">✏️</button>
                <button class="icon-btn del"  onclick="deleteInvoice(${i.id})" title="Delete">🗑️</button>
              </div>
            </td>
          </tr>`;
      }).join('')
    : `<tr><td colspan="7"><div class="empty"><div class="empty-icon">🧾</div>No invoices found</div></td></tr>`;
}

function renderAudit() {
  const actionColor = { INSERT: 'green', UPDATE: 'orange', DELETE: 'red' };
  document.getElementById('audit-body').innerHTML = auditLog.map(l => `
    <tr>
      <td><span style="color:var(--muted);font-size:12px">#${l.id}</span></td>
      <td><strong>${l.table}</strong></td>
      <td><span class="badge badge-${actionColor[l.action] || 'gray'}">${l.action}</span></td>
      <td>${l.recordId}</td>
      <td style="color:var(--muted);font-size:12px">${l.time}</td>
      <td style="font-size:12.5px">${l.notes}</td>
    </tr>`).join('');
}

function renderDashboard() {
  document.getElementById('stat-patients').textContent     = patients.length;
  document.getElementById('stat-doctors').textContent      = doctors.length;
  document.getElementById('stat-appointments').textContent = appointments.length;

  const revenue = invoices.reduce((s, i) => s + i.amount, 0);
  document.getElementById('stat-revenue').textContent = fmtAmount(revenue);

  // Upcoming (Scheduled) appointments
  const upcoming = appointments
    .filter(a => a.status === 'Scheduled')
    .sort((a, b) => a.date < b.date ? -1 : 1)
    .slice(0, 5);

  document.getElementById('dash-appointments').innerHTML = upcoming.length
    ? upcoming.map(a => {
        const p = getPatient(a.patientId), d = getDoctor(a.doctorId);
        return `
          <div class="appt-item">
            <div class="appt-time">${a.time}</div>
            <div class="appt-info">
              <div class="appt-name">${p?.name || '—'}</div>
              <div class="appt-doc">${d?.name || '—'} · ${a.date}</div>
            </div>
            ${statusBadge(a.status)}
          </div>`;
      }).join('')
    : '<div class="empty"><div class="empty-icon">📅</div>No upcoming appointments</div>';

  // Recent audit activity
  document.getElementById('dash-activity').innerHTML = auditLog.slice(0, 5).map(l => `
    <div class="activity-item">
      <div class="activity-dot" style="background:${
        l.action === 'INSERT' ? 'var(--teal)' :
        l.action === 'UPDATE' ? 'var(--accent)' : 'var(--red)'
      }"></div>
      <div>
        <div class="activity-text"><strong>${l.action}</strong> on <strong>${l.table}</strong> #${l.recordId}</div>
        <div class="activity-time">${l.time}</div>
      </div>
    </div>`).join('');
}

// ══ INIT ══
document.getElementById('topbar-date').textContent = new Date().toLocaleDateString('en-US', {
  weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
});

loadAllData();

// Close modal when clicking outside
document.querySelectorAll('.modal-overlay').forEach(overlay => {
  overlay.addEventListener('click', e => {
    if (e.target === overlay) overlay.classList.remove('open');
  });
});