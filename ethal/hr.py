import frappe
from datetime import date, timedelta, datetime

@frappe.whitelist()
def before_submit_leave_allocation(doc, method):
    def calculate_years_of_experience(doj, till_date=None):
        from dateutil.relativedelta import relativedelta
        if not till_date:
            from datetime import datetime 
            till_date = datetime.today()

        try: 
            experience = relativedelta(till_date, doj).years
        except AttributeError:
            experience = 0
        
        return experience

    doj = frappe.db.get_value('Employee', doc.employee, 'date_of_joining')
    leave_date = frappe.db.get_value('Leave Allocation', doc.name, 'from_date')
    total_experience = calculate_years_of_experience(doj, leave_date)
    base_leave_count = 16
    get_total_leaves = base_leave_count+(float(total_experience)/2)
    frappe.db.set_value('Leave Allocation', doc.name, 'new_leaves_allocated', get_total_leaves)
    frappe.db.set_value('Leave Allocation', doc.name, 'total_leaves_allocated', get_total_leaves)

@frappe.whitelist()
def calculate_overtime_in_salary_slip(doc, method):
    overtime_applicable = frappe.db.get_value('Employee', doc.employee, 'is_overtime_applicable')
    if overtime_applicable:
        daily_overtime(doc)
        sunday_overtime(doc)
        holiday_overtime(doc)
    # process_auto_attendance_for_holidays(doc)

def daily_overtime(doc):
    holiday = frappe.db.get_all('Holiday', filters={'holiday_date': ('between',[ doc.start_date, doc.end_date])},  fields=['holiday_date'], as_list=1)
   
    holiday_ = []
    for i in holiday:
        splitdate = i[0].strftime('%Y-%m-%d')
        holiday_.append(splitdate)

    filters = [
        ['employee', '=', doc.employee],
        ['attendance_date', '<=', doc.end_date],
        ['attendance_date', '>=', doc.start_date],
        ['attendance_date', 'not in', holiday_],
        ['docstatus', '!=', 2],
        ['status', '=', 'Present']
    ]

    attendances = frappe.db.get_all('Attendance', filters=filters, fields=['working_hours'], as_list=True)
    attendance_list = []
    for i in attendances:
        for j in i:
            attendance_list.append(j)
   
    shift = frappe.db.get_value('Employee', {'employee': doc.employee, 'is_overtime_applicable': 1}, ['default_shift'])
    if shift: 
        shift_start = frappe.db.get_value('Shift Type',shift,'start_time')
        shift_end = frappe.db.get_value('Shift Type',shift,'end_time')
        shift_start_hours = shift_start.seconds//3600
        shift_end_hours = shift_end.seconds//3600

        shift_time = shift_end_hours - shift_start_hours
        for i in attendance_list:
            # i = int(i)
            if i > shift_time:
                doc.normal_ot_hours = doc.normal_ot_hours + (i - shift_time)
                
def sunday_overtime(doc):
   
    holiday = frappe.db.get_all('Holiday', filters={'description': 'Sunday', 'holiday_date': ('between',[ doc.start_date, doc.end_date])},  fields=['holiday_date'], as_list=1)
   
    holiday_ = []
    for i in holiday:
        splitdate = i[0].strftime('%Y-%m-%d')
        holiday_.append(splitdate)
  
    filters = [
        ['employee', '=', doc.employee],
        ['attendance_date', 'in', holiday_],
        ['docstatus', '!=', 2],
        ['status', '=', 'Present']
    ]
   
    attendances = frappe.db.get_all('Attendance', filters=filters, fields=['attendance_date'], as_list=True)
    attendance_ = []
    if attendances: 
        for i in attendances:
            splitdate = i[0].strftime('%Y-%m-%d')
            attendance_.append(splitdate +' 00:00:00')
    for i in attendance_:
        start_date = i
        end_date = datetime.strptime(i, '%Y-%m-%d %H:%M:%S')
        end_date = end_date + timedelta(days=1)
        midnight_checkout = frappe.db.sql(""" select time from `tabEmployee Checkin` where time between '{0}' and '{1}';
        """.format(start_date, end_date), as_list=True)
        date = []
        for i in midnight_checkout:
            for j in i:
                date.append(j)
        differences = date[1] - date[0]
        hours = differences.seconds//3600
        minutes = (differences.seconds//60)%60
        minutes = minutes /100

        # frappe.throw('ja na be')
        doc.sunday_ot_hours += hours+minutes       
        # for i in attendances:
        #     print(i.working_hours)
        #     doc.sunday_ot_hours += i.working_hours

def holiday_overtime(doc):
    sunday = frappe.db.get_all('Holiday', filters={'description': ['!=','Sunday'], 'holiday_date': ('between',[ doc.start_date, doc.end_date])},  fields=['holiday_date'], as_list=1)
   
    sunday_ = []
    for i in sunday:
        splitsundaydate = i[0].strftime('%Y-%m-%d')
        sunday_.append(splitsundaydate)
    
    holiday = frappe.db.get_all('Holiday', filters={'holiday_date': ['in', sunday_]},  fields=['holiday_date'], as_list=1)
    holiday_ = []
    for i in holiday:
        splitholidaydate = i[0].strftime('%Y-%m-%d')
        holiday_.append(splitholidaydate)
    
    filters = [
        ['employee', '=', doc.employee],
        ['attendance_date', 'in', holiday_],
        ['docstatus', '!=', 2],
        ['status', '=', 'Present']
    ]
    
    attendances = frappe.db.get_all('Attendance', filters=filters, fields=['attendance_date'], as_list=True)
    attendance_ = []
    if attendances: 
        for i in attendances:
            splitdate = i[0].strftime('%Y-%m-%d')
            attendance_.append(splitdate +' 00:00:00')
    for i in attendance_:
        start_date = i
        end_date = datetime.strptime(i, '%Y-%m-%d %H:%M:%S')
        end_date = end_date + timedelta(days=1)
        midnight_checkout = frappe.db.sql(""" select time from `tabEmployee Checkin` where time between '{0}' and '{1}';
        """.format(start_date, end_date), as_list=True)
        date = []
        for i in midnight_checkout:
            for j in i:
                date.append(j)
        differences = date[1] - date[0]
        hours = differences.seconds//3600
        minutes = (differences.seconds//60)%60
        minutes = minutes /100
        doc.holiday_ot_hours_ += hours+minutes
