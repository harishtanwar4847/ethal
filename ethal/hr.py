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
        # night_overtime(doc)
        sunday_overtime(doc)
        holiday_overtime(doc)
    # process_auto_attendance_for_holidays(doc)

@frappe.whitelist()
def on_update_employee(doc, method):
    get_salary_structure_ass = frappe.get_all('Salary Structure Assignment', filters={'employee': doc.employee, 'docstatus': 1})
    if get_salary_structure_ass:
        grade = frappe.db.get_value('Employee Grade', doc.grade, 'default_salary_structure')
        frappe.db.set_value('Salary Structure Assignment', {'name': get_salary_structure_ass[0].name}, 'salary_structure', grade)
        employee_grade = frappe.db.get_value('Employee Grade', doc.grade, 'base_amount')
        frappe.db.set_value('Salary Structure Assignment', {'name': get_salary_structure_ass[0].name}, 'base', employee_grade)
        frappe.db.set_value('Salary Structure Assignment', {'name': get_salary_structure_ass[0].name}, 'salary_in_usd', employee_grade)
        frappe.db.set_value('Salary Structure Assignment', {'name': get_salary_structure_ass[0].name}, 'staus', 'Salary Updated')
        frappe.db.commit()

def daily_overtime(doc):
    holiday = frappe.db.get_all('Holiday', filters={'holiday_date': ('between',[ doc.start_date, doc.end_date])},  fields=['holiday_date'], as_list=1)
   
    holiday_ = []
    for i in holiday:
        splitdate = i[0].strftime('%Y-%m-%d')
        holiday_.append(splitdate)
    shift = frappe.db.get_value('Employee', {'employee': doc.employee}, ['default_shift'])
    if shift: 

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
    
        # shift_start = frappe.db.get_value('Shift Type',shift,'start_time')
        # shift_end = frappe.db.get_value('Shift Type',shift,'end_time')
        # shift_time = shift_end - shift_start
        # hours = shift_time.seconds//3600
        hours = 8
        print(hours)
        for i in attendance_list:
            # i = int(i)
            print(i)
            if i > hours:
                doc.normal_ot_hours += (i - hours)
                
# def night_overtime(doc):
#     holiday = frappe.db.get_all('Holiday', filters={'holiday_date': ('between',[ doc.start_date, doc.end_date])},  fields=['holiday_date'], as_list=1)
   
#     holiday_ = []
#     for i in holiday:
#         splitdate = i[0].strftime('%Y-%m-%d')
#         holiday_.append(splitdate)
#     # shift = frappe.db.get_value('Employee', {'employee': doc.employee, 'is_overtime_applicable': 1}, ['default_shift'])
#     # if shift: 

#     filters = [
#         ['employee', '=', doc.employee],
#         ['attendance_date', '<=', doc.end_date],
#         ['attendance_date', '>=', doc.start_date],
#         ['attendance_date', 'not in', holiday_],
#         ['docstatus', '!=', 2],
#         ['status', '=', 'Present'],
#         ['shift', '=', 'Night shift']
#     ]

#     attendances = frappe.db.get_all('Attendance', filters=filters, fields=['working_hours'], as_list=True)
#     attendance_list = []
#     for i in attendances:
#         for j in i:
#             attendance_list.append(j)
#     print('attendance', attendances)
#     shift_start = frappe.db.get_value('Shift Type','Night shift','start_time')
#     shift_end = frappe.db.get_value('Shift Type','Night shift','end_time')
#     shift_time = shift_end - shift_start
#     hours = shift_time.seconds//3600
#     for i in attendance_list:
#         print('time',i)
#         # i = int(i)
#         if i > hours:
#             doc.night_ot_hours +=  (i - hours)
    
def sunday_overtime(doc):
   
    holiday = frappe.db.get_all('Holiday', filters={'description': 'Sunday', 'holiday_date': ('between',[ doc.start_date, doc.end_date])},  fields=['holiday_date'], as_list=1)
   
    holiday_ = []
    for i in holiday:
        splitdate = i[0].strftime('%Y-%m-%d')
        holiday_.append(splitdate)

    # shift = frappe.db.get_value('Employee', {'employee': doc.employee, 'is_overtime_applicable': 1}, ['default_shift'])
    # if shift:   

    filters = [
        ['employee', '=', doc.employee],
        ['attendance_date', 'in', holiday_],
        ['docstatus', '!=', 2],
        ['status', '=', 'Present']
    ]
    
    attendances = frappe.db.get_all('Attendance', filters=filters, fields=['working_hours'], as_list=True)
    for i in attendances:    
        doc.sunday_ot_hours += i[0]
       
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
    
    attendances = frappe.db.get_all('Attendance', filters=filters, fields=['working_hours'], as_list=True)
    for i in attendances:
        doc.holiday_ot_hours_ += i[0]

@frappe.whitelist()
def trigger_mail_if_absent_consecutive_5_days(doc, method):

    attendance = frappe.db.sql("""
    select count(attendance_date) as count
    from `tabAttendance` 
    where  attendance_date >= DATE_SUB(CURDATE(), INTERVAL 5 DAY) 
    and status in ('Absent', 'On Leave') and docstatus = 1 and employee='{}' order by attendance_date;

    """.format(doc.employee), as_dict = 1)
    print(attendance)
    if attendance[0]['count'] == 4:
        notification = frappe.get_doc('Notification', 'Consecutive Leave')

        args={'doc': doc}
        recipients = notification.get_list_of_recipients(doc, args)
        recipients_list = list(recipients[0])
        message = 'Alert! {} has been on Leave for 5 consecutive days.'.format(doc.employee_name)
        get_employee_warnings = frappe.get_all('Warning Letter Detail', filters={'parent': doc.employee}, fields=['warning_number'], order_by='warning_number desc', page_length=1)
        print('get employees', get_employee_warnings)
        warning_template = frappe.db.get_value('Warning Letter Template', 'Consecutive Leave', 'name')
        print(warning_template)
        warning_letter = frappe.new_doc('Warning Letter')
        warning_letter.employee = doc.employee
        warning_letter.template = warning_template

        if not get_employee_warnings:
            # frappe.throw('ja na be')
            warning_letter.warning_number = 1
           
        else:
            warning_letter.warning_number = get_employee_warnings[0]['warning_number'] + 1
           
        warning_letter.save(ignore_permissions=True)

        set_employee_warnings = frappe.get_doc('Employee', doc.employee)
        set_employee_warnings.append('warnings', {
            'warning_letter': warning_letter.name
        })
        if not get_employee_warnings:
            set_employee_warnings.warnings_status = 1
        else:
            set_employee_warnings.warnings_status = get_employee_warnings[0]['warning_number']+1
        set_employee_warnings.save(ignore_permissions=True)

        for user in recipients_list:
            frappe.publish_realtime(event='msgprint',message=message,user=user)
        frappe.enqueue(method=frappe.sendmail, recipients=recipients_list, sender=None, now=True,
        subject=frappe.render_template(notification.subject, args), message=frappe.render_template(notification.message, args))

@frappe.whitelist()
def update_salary_structure_assignment_rate(doc, method):
    employee_list = frappe.db.get_all('Payroll Employee Detail', {'parent': doc.name}, ['employee'], as_list=1)
    if employee_list:
        for i in employee_list:
            get_base_amount = frappe.db.get_value('Salary Structure Assignment', {'employee': i[0]}, 'base')
            if get_base_amount:
                frappe.db.set_value('Salary Structure Assignment', {'employee': i[0]}, 'salary_in_birr', int(get_base_amount) * int(doc.conversion_rate))
                frappe.db.commit()

def shift_rotate():
    print("rotate shift method call")
    female_employee = frappe.db.get_all('Employee', filters = {'gender': 'Female', 'shift_rotate': 1}, fields=['name'], as_list=1)
    if female_employee:
        female_employee_store_in_list = [i[0] for i in female_employee]
        female_employee_convert_tuple = tuple(female_employee_store_in_list)
        print(female_employee_convert_tuple)
        frappe.db.sql("""
                        Update `tabEmployee` 
                        SET default_shift = CASE 
                        WHEN default_shift='A' THEN 'B' 
                        WHEN default_shift='B' THEN 'A' 
                        ELSE default_shift END where employee in {}
                        """.format(female_employee_convert_tuple))
        frappe.db.commit()

    male_employee = frappe.db.get_all('Employee', filters = {'gender': 'Male','shift_rotate': 1}, fields=['name'], as_list=1)
    if male_employee:
        male_employee_store_in_list = [i[0] for i in male_employee]
        male_employee_convert_tuple = tuple(male_employee_store_in_list)
        frappe.db.sql("""
                        Update `tabEmployee`
                        SET default_shift = CASE 
                        WHEN default_shift='A' THEN 'B' 
                        WHEN default_shift='B' THEN 'C' 
                        WHEN default_shift='C' THEN 'A' 
                        ELSE default_shift END where employee in {} 
                        """.format(male_employee_convert_tuple))
        frappe.db.commit()

@frappe.whitelist()
def before_insert_salary_structure_assignment(doc, method):
    get_employee_base_amount = frappe.db.get_value('Employee Grade', {'default_salary_structure': doc.salary_structure}, 'base_amount')
    frappe.db.set_value('Salary Structure Assignment', {'name': doc.name}, 'base', get_employee_base_amount)
    frappe.db.commit()        