import mysql.connector
from database import connect_to_database


def get_daily_appointments_report():
    """
    Fetches today's appointments using the DailyAppointments view.
    """
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM DailyAppointments")
            results = cursor.fetchall()

            print(f"\n--- DAILY APPOINTMENTS REPORT ({len(results)} records) ---")
            if not results:
                print("No appointments scheduled for today.")
            else:
                for row in results:
                    print(f"ID: {row['AppointmentID']} | Patient: {row['PatientName']} "
                          f"| Doctor: {row['DoctorName']} | Dept: {row['DepartmentName']} "
                          f"| Time: {row['AppointmentTime']} | Status: {row['Status']}")
            return results
        finally:
            cursor.close()
            conn.close()


def get_financial_summary():
    """
    Generates a financial summary using the PatientInvoiceSummary view.
    Shows total billed, collected, and outstanding per patient.
    """
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM PatientInvoiceSummary ORDER BY TotalOutstanding DESC")
            results = cursor.fetchall()

            # Overall totals
            total_billed      = sum(r['TotalBilled']      for r in results)
            total_paid        = sum(r['TotalPaid']        for r in results)
            total_outstanding = sum(r['TotalOutstanding'] for r in results)

            print("\n--- FINANCIAL SUMMARY REPORT ---")
            print(f"{'Patient':<20} {'Invoices':>8} {'Billed':>10} {'Paid':>10} {'Outstanding':>12}")
            print("-" * 65)
            for row in results:
                print(f"{row['PatientName']:<20} "
                      f"{row['TotalInvoices']:>8} "
                      f"${row['TotalBilled']:>9.2f} "
                      f"${row['TotalPaid']:>9.2f} "
                      f"${row['TotalOutstanding']:>11.2f}")
            print("-" * 65)
            print(f"{'TOTAL':<20} {'':>8} ${total_billed:>9.2f} ${total_paid:>9.2f} ${total_outstanding:>11.2f}")
            return results
        finally:
            cursor.close()
            conn.close()


def get_monthly_revenue_report(year, month):
    """
    Generates a detailed monthly revenue report using the
    MonthlyRevenueReport stored procedure.
    Shows each invoice for the given month and an aggregated summary.
    """
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.callproc('MonthlyRevenueReport', (year, month))

            print(f"\n--- MONTHLY REVENUE REPORT: {month:02d}/{year} ---")

            result_sets = list(cursor.stored_results())

            # First result set: detailed invoice list
            if len(result_sets) > 0:
                invoices = result_sets[0].fetchall()
                if invoices:
                    print(f"\n{'Patient':<20} {'Date':<12} {'Amount':>10} {'Status':<15}")
                    print("-" * 60)
                    for inv in invoices:
                        print(f"{inv['PatientName']:<20} "
                              f"{str(inv['InvoiceDate']):<12} "
                              f"${inv['TotalAmount']:>9.2f} "
                              f"{inv['PaymentStatus']:<15}")
                else:
                    print("No invoices found for this period.")

            # Second result set: aggregated summary
            if len(result_sets) > 1:
                summary = result_sets[1].fetchone()
                if summary:
                    print(f"\n{'--- SUMMARY ---':}")
                    print(f"Total Invoices    : {summary['TotalInvoices']}")
                    print(f"Gross Revenue     : ${summary['GrossRevenue']:.2f}")
                    print(f"Collected Revenue : ${summary['CollectedRevenue']:.2f}")
                    print(f"Outstanding       : ${summary['OutstandingRevenue']:.2f}")

            return result_sets
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()


def get_patient_statistics():
    """
    Generates statistics on patient visits per department.
    """
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT d.DepartmentName, COUNT(a.AppointmentID) AS VisitCount
                FROM Departments d
                LEFT JOIN Doctors doc ON d.DepartmentID = doc.DepartmentID
                LEFT JOIN Appointments a ON doc.DoctorID = a.DoctorID
                GROUP BY d.DepartmentName
                ORDER BY VisitCount DESC
            """
            cursor.execute(query)
            stats = cursor.fetchall()

            print("\n--- PATIENT VISITS BY DEPARTMENT ---")
            print(f"{'Department':<25} {'Visits':>8}")
            print("-" * 35)
            for entry in stats:
                print(f"{entry['DepartmentName']:<25} {entry['VisitCount']:>8}")
            return stats
        finally:
            cursor.close()
            conn.close()


def get_audit_log(limit=20):
    """
    Displays the most recent entries from the AuditLog table.
    AuditLog is populated automatically by triggers:
      - AfterInvoiceInsert   : logs every new invoice
      - AfterAppointmentUpdate: logs every appointment status change
    """
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM AuditLog ORDER BY ChangedAt DESC LIMIT %s"
            cursor.execute(query, (limit,))
            logs = cursor.fetchall()

            print(f"\n--- AUDIT LOG (latest {limit} entries) ---")
            if not logs:
                print("Audit log is empty. Logs are generated automatically when invoices are created or appointment statuses change.")
            else:
                print(f"{'ID':>4} {'Table':<15} {'Action':<10} {'RecordID':>8} {'Changed At':<20} Notes")
                print("-" * 80)
                for log in logs:
                    print(f"{log['LogID']:>4} "
                          f"{log['TableName']:<15} "
                          f"{log['Action']:<10} "
                          f"{str(log['RecordID']):>8} "
                          f"{str(log['ChangedAt']):<20} "
                          f"{log['Notes']}")
            return logs
        finally:
            cursor.close()
            conn.close()