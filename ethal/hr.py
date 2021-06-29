import frappe
from frappe.utils import getdate, nowdate, cint, flt
import json
from datetime import date, timedelta, datetime
from frappe.utils import add_days, cint, cstr, flt, getdate, rounded, date_diff, money_in_words
import time
from frappe.utils import formatdate
import ast
import itertools
from erpnext.hr.doctype.employee_checkin.employee_checkin import mark_attendance_and_link_log
from frappe.utils.background_jobs import enqueue

def override_job_applicant_dashboard(data):
    print(data)
    return {
        'fieldname': 'job_applicant',
        'transactions': [
            # {
            #     'items': ['Employee', 'Employee Onboarding']
            # },
            # {
            #     'items': ['Job Offer']
            # },
            # {
            #     'items': ['Interview']
            # },
        ],
    }

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
def set_conversion_rate(employee):
    if employee:
        employee_list = frappe.db.get_all('Payroll Employee Detail', {'employee': employee}, ['parent'], order_by='creation desc', limit=1, as_list=1)
        if employee_list:
            get_conversion_rate = frappe.db.get_value('Payroll Entry', employee_list[0][0], 'conversion_rate')
            return get_conversion_rate

def before_save_salary_slip(doc, method):
    doc.normal_ot_hours = 0
    doc.sunday_ot_hours = 0
    doc.holiday_ot_hours_ = 0
    doc.total_working_days = 0
    doc.paid_leaves = 0
    doc.total_incentives = 0

    overtime_applicable = frappe.db.get_value('Employee', doc.employee, 'is_overtime_applicable')
    if overtime_applicable:
        daily_overtime(doc)
        sunday_overtime(doc)
        holiday_overtime(doc)

    before_save(doc, method)

def before_insert_salary_slip(doc, method):
    doc.normal_ot_hours = 0
    doc.sunday_ot_hours = 0
    doc.holiday_ot_hours_ = 0
    doc.total_working_days = 0
    doc.paid_leaves = 0
    doc.total_incentives = 0

    absent_attendances = frappe.get_list('Attendance', [
        ['employee', '=', doc.employee],
        ['attendance_date', 'between', [doc.start_date, doc.end_date]],
        ['status', 'in', ['Absent', 'Half Day']],
        ['docstatus', '=', 1],
        ['leave_application', 'is', 'not set']
    ])

    for i in absent_attendances:
        process_lop_leave_for_attendance(i.name)

    doc.get_leave_details()

    overtime_applicable = frappe.db.get_value('Employee', doc.employee, 'is_overtime_applicable')
    if overtime_applicable:
        daily_overtime(doc)
        sunday_overtime(doc)
        holiday_overtime(doc)

def before_save(doc, method):
    if doc.employee:
        company = frappe.defaults.get_user_default("company") 
        default_holiday = frappe.db.get_value('Company', company, 'default_holiday_list')
        holiday_ = []
        if default_holiday:
            holiday_day = frappe.db.get_value('Holiday List', {'name': default_holiday}, 'weekly_off')
            holiday = frappe.db.get_all('Holiday', filters={'parent': default_holiday, 'description': holiday_day, 'holiday_date': ('between',[ doc.start_date, doc.end_date])},  fields=['holiday_date'], as_list=1)

            for i in holiday:
                splitdate = i[0].strftime('%Y-%m-%d')
                holiday_.append(splitdate)
                
            total = date_diff(doc.end_date, doc.start_date) + 1   
            hr_settings = frappe.db.get_single_value('HR Settings', 'include_holidays_in_total_working_days')
            if hr_settings == 0: 
                doc.total_working_days = total - len(holiday_)
                doc.payment_days = doc.total_working_days - doc.leave_without_pay
            else:
                doc.total_working_days = total
                doc.payment_days = doc.total_working_days - doc.leave_without_pay
            paid_leaves = frappe.db.get_all('Leave Application', filters={'leave_type': ['!=', 'Leave Without Pay'], 'docstatus': ['=', 1], 'from_date': ['>=', doc.start_date], 'to_date': ['<=', doc.end_date]}, fields=['count(name) as total'])
            if paid_leaves:
                doc.paid_leaves = paid_leaves[0]['total']   
            employee_incentive = frappe.db.sql("""
                    select sum(eibd.incentive_hours) from `tabEmployee Incentive Bulk Detail` as eibd 
                    join `tabEmployee Incentive Bulk` as eib on eibd.parent = eib.name
                    where eib.incentive_date between '{0}' and '{1}' and eibd.employee = '{2}' and eib.docstatus = 1
            """.format(doc.start_date, doc.end_date, doc.employee))
            if employee_incentive:
                doc.total_incentives = employee_incentive[0][0]

            doc.calculate_component_amounts("earnings")
            doc.calculate_component_amounts("deductions")
            
def process_lop_leave_for_attendance(attendance_name):
    attendance = frappe.get_doc('Attendance', attendance_name)

    pending_leave_applications = frappe.get_list('Leave Application', [
        ['employee', '=', attendance.employee],
        ['docstatus', '=', 0],
        ['status', '=', 'Open'],
        ['from_date', '<=', attendance.attendance_date],
        ['to_date', '>=', attendance.attendance_date]
    ])

    for i in pending_leave_applications:
        leave_application = frappe.get_doc('Leave Application', i.name)
        leave_application.docstatus = 0
        leave_application.status = 'Rejected'
        leave_application.workflow_state = 'Rejected'
        leave_application.save()

    leave_application = frappe.new_doc('Leave Application')
    leave_application.employee = attendance.employee
    leave_application.company = attendance.company
    leave_application.from_date = attendance.attendance_date.strftime('%Y-%m-%d')
    leave_application.to_date = attendance.attendance_date.strftime('%Y-%m-%d')
    leave_application.half_day = 1 if attendance.status == 'Half Day' else 0
    leave_application.leave_type = 'Leave Without Pay'
    leave_application.insert()

    leave_application.reload()
    leave_application.docstatus = 1
    leave_application.status = 'Approved'
    leave_application.workflow_state = 'Approved'
    leave_application.save()

    frappe.db.commit()
    # process_auto_attendance_for_holidays(doc)

@frappe.whitelist()
def on_update_employee(doc, method):
    get_salary_structure_ass = frappe.get_all('Salary Structure Assignment', filters={'employee': doc.employee, 'docstatus': 1})
    if get_salary_structure_ass:
        # grade = frappe.db.get_value('Employee Grade', doc.grade, 'default_salary_structure')
        # frappe.db.set_value('Salary Structure Assignment', {'name': get_salary_structure_ass[0].name}, 'salary_structure', grade)
        employee_grade = frappe.db.get_value('Employee Grade', doc.grade, 'base_amount')
        if employee_grade:
            frappe.db.set_value('Salary Structure Assignment', {'name': get_salary_structure_ass[0].name}, 'grade', doc.grade)
            frappe.db.set_value('Salary Structure Assignment', {'name': get_salary_structure_ass[0].name}, 'base', employee_grade)
            frappe.db.set_value('Salary Structure Assignment', {'name': get_salary_structure_ass[0].name}, 'salary_in_usd', employee_grade)
            frappe.db.set_value('Salary Structure Assignment', {'name': get_salary_structure_ass[0].name}, 'staus', 'Salary Updated')
            frappe.db.commit()

def daily_overtime(doc):
    employee_holiday = frappe.db.get_value('Employee', doc.employee, 'holiday_list')
    holiday = frappe.db.get_all('Holiday', filters={'parent': employee_holiday, 'holiday_date': ('between',[ doc.start_date, doc.end_date])},  fields=['holiday_date'], as_list=1)
    
    holiday_ = []
    for i in holiday:
        splitdate = i[0].strftime('%Y-%m-%d')
        holiday_.append(splitdate)
    # shift = frappe.db.get_value('Employee', {'employee': doc.employee}, ['default_shift'])
    # if shift: 

    filters = [
        ['employee', '=', doc.employee],
        ['attendance_date', '<=', doc.end_date],
        ['attendance_date', '>=', doc.start_date],
        ['attendance_date', 'not in', holiday_],
        ['docstatus', '!=', 2],
        ['status', '=', 'Present']
    ]

    attendances = frappe.db.get_all('Attendance', filters=filters, fields=['working_hours', 'shift', 'attendance_date'], as_list=True)
    
    for i in attendances:
        print(i)
        shift_start = frappe.db.get_value('Shift Type',i[1],'start_time')
        shift_end = frappe.db.get_value('Shift Type',i[1],'end_time')
        if shift_end is not None and shift_start is not None:
            shift_time = shift_end - shift_start
            hours = shift_time.seconds
            total = hours/3600
            day = i[2].strftime('%A')
            if (i[1] == 'Night shift' and i[0] > total and day == 'Saturday'):
                doc.sunday_ot_hours += (i[0] - total)
            elif (i[1] == 'Night shift' and i[0] > total and day != 'Saturday'):
                doc.normal_ot_hours += (i[0] - total)
            elif (i[1] != 'Night shift' and i[0] > total):
                doc.normal_ot_hours += (i[0] - total)
    # frappe.throw('ja na')   
                
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
    employee_holiday = frappe.db.get_value('Employee', doc.employee, 'holiday_list')
    holiday_day = frappe.db.get_value('Holiday List', {'name': employee_holiday}, 'weekly_off')
    holiday = frappe.db.get_all('Holiday', filters={'parent': employee_holiday, 'description': holiday_day, 'holiday_date': ('between',[ doc.start_date, doc.end_date])},  fields=['holiday_date'], as_list=1)
   
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
    
    attendances = frappe.db.get_all('Attendance', filters=filters, fields=['working_hours'], as_list=True)
    for i in attendances:    
        doc.sunday_ot_hours += i[0]
       
def holiday_overtime(doc):
    employee_holiday = frappe.db.get_value('Employee', doc.employee, 'holiday_list')
    holiday_day = frappe.db.get_value('Holiday List', {'name': employee_holiday}, 'weekly_off')
    holiday = frappe.db.get_all('Holiday', filters={'parent': employee_holiday, 'description': ['!=', holiday_day], 'holiday_date': ('between',[ doc.start_date, doc.end_date])},  fields=['holiday_date'], as_list=1)
   
    holiday_ = []
    for i in holiday:
        splitsundaydate = i[0].strftime('%Y-%m-%d')
        holiday_.append(splitsundaydate)
    
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
    if doc.conversion_rate != 0:
        employee_list = frappe.db.get_all('Payroll Employee Detail', {'parent': doc.name}, ['employee'], as_list=1)
        if employee_list:
            for i in employee_list:
                get_base_amount = frappe.db.get_value('Salary Structure Assignment', {'employee': i[0], 'docstatus': ['!=', 2]}, 'base')
                if get_base_amount:
                    frappe.db.set_value('Salary Structure Assignment', {'employee': i[0], 'docstatus': ['!=', 2]}, 'salary_in_birr', float(get_base_amount) * doc.conversion_rate)
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

def get_employees(doc, **kwargs):
    conditions, values = [], []
    for field, value in kwargs.items():
        if value:
            conditions.append("{0}=%s".format(field))
            values.append(value)

    condition_str = " and " + " and ".join(conditions) if conditions else ""

    employees = frappe.db.sql_list("select name from tabEmployee where status='Active' {condition}"
        .format(condition=condition_str), tuple(values))

    return employees

@frappe.whitelist()
def before_insert_salary_structure_assignment(doc, method):
    # get_employee_base_amount = frappe.db.get_value('Employee Grade', {'default_salary_structure': doc.salary_structure}, 'base_amount')
    # if get_employee_base_amount:
    #     frappe.db.set_value('Salary Structure Assignment', {'name': doc.name}, 'base', get_employee_base_amount)
    #     frappe.db.commit()   
    if doc.base:
        frappe.db.set_value('Salary Structure Assignment', {'name': doc.name}, 'salary_in_usd', doc.base)

@frappe.whitelist()
def assign_salary_structure(doc, company=None, grade=None, department=None, designation=None,employee=None,
        from_date=None, base=None, variable=None, income_tax_slab=None):
    employees = get_employees(doc, company= company, grade= grade,department= department,designation= designation,name=employee)

    if employees:
        print('in if')
        if len(employees) > 20:
            frappe.enqueue(assign_salary_structure_for_employees, timeout=600,
                employees=employees, salary_structure=doc,from_date=from_date,
            base=base, variable=variable, income_tax_slab=income_tax_slab)
        else:
            assign_salary_structure_for_employees(employees, doc, from_date=from_date,
                base=base, variable=variable, income_tax_slab=income_tax_slab)
    else:
        frappe.msgprint(frappe._("No Employee Found"))

def assign_salary_structure_for_employees(employees, salary_structure, from_date=None, base=None, variable=None, income_tax_slab=None):
    print('in assign method')
    salary_structures_assignments = []
    existing_assignments_for = get_existing_assignments(employees, salary_structure, from_date)
    count=0
    for employee in employees:
        if employee in existing_assignments_for:
            continue
        count +=1

        salary_structures_assignment = create_salary_structures_assignment(employee,
            salary_structure, from_date, base, variable, income_tax_slab)
        salary_structures_assignments.append(salary_structures_assignment)
        frappe.publish_progress(count*100/len(set(employees) - set(existing_assignments_for)), title = frappe._("Assigning Structures..."))

    if salary_structures_assignments:
        frappe.msgprint(frappe._("Structures have been assigned successfully"))


def create_salary_structures_assignment(employee, salary_structure, from_date, base, variable, income_tax_slab=None):
    salary_structure = ast.literal_eval(salary_structure)
    assignment = frappe.new_doc("Salary Structure Assignment")
    assignment.employee = employee
    assignment.salary_structure = salary_structure['name']
    assignment.company = salary_structure['company']
    assignment.from_date = from_date
    assignment.base = base
    assignment.variable = variable
    assignment.income_tax_slab = income_tax_slab
    assignment.save(ignore_permissions = True)
    assignment.submit()
    return assignment.name

def get_existing_assignments(employees, salary_structure, from_date):
    salary_structure = ast.literal_eval(salary_structure)
    salary_structures_assignments = frappe.db.sql_list("""
        select distinct employee from `tabSalary Structure Assignment`
        where salary_structure=%s and employee in (%s)
        and company= %s and docstatus=1
    """ % ('%s', ', '.join(['%s']*len(employees)),'%s'), [salary_structure['name']] + employees+[salary_structure['company']])
    if salary_structures_assignments:
        frappe.msgprint(frappe._("Skipping Salary Structure Assignment for the following employees, as Salary Structure Assignment records already exists against them. {0}")
            .format("\n".join(salary_structures_assignments)))
    return salary_structures_assignments

@frappe.whitelist()
def existing_interview_rounds(job_applicant, job_opening):
    interview = frappe.get_list('Interview', filters={'job_applicant': job_applicant}, as_list = 1)
    if len(interview) > 0:
        rounds = frappe.get_list('Interview Round', filters={'interview': interview[0][0]}, order_by='round_number')
        print(len(rounds))
        if len(rounds) > 0:
            return True
        else:
            return False

@frappe.whitelist()
def get_interview_rounds(job_applicant, job_opening):
    interview = frappe.get_all('Interview', filters={'job_applicant': job_applicant, }, as_list = 1)
    rounds = frappe.get_all('Interview Round', filters={'interview': interview[0][0]}, fields=['*'], order_by='round_number')
    print(rounds)
    list2 = []
    for i in rounds:
        comment = []
        if i['_comments'] is not None:
            a = json.loads(i['_comments'])
            for j in a:
                comment.append(j['comment'])
            
        print(comment)
       
        interviewer = frappe.get_all('Interviewer', filters={'parent': i['name']}, fields=['employee', 'employee_name'] )
        l_ = []
        for row in interviewer:
                l_.append("{}-{}".format(row['employee'], row['employee_name']))    
        k =  [
                # {
                #     'label': i['round_number'],
                #     'fieldname': '',
                #     'fieldtype': 'Section Break'
                # },
                {
                    'label': 'Round Number',
                    'fieldname': 'round_number',
                    'fieldtype': 'Data',
                    'default': i['round_number'],
                    'read_only': 1
                },
                {
                    'label': 'Date',
                    'fieldname': 'date',
                    'fieldtype': 'Datetime',
                    'read_only': 1,
                    'default': i['date']
                },
                {
                    'label': '',
                    'fieldname': '',
                    'fieldtype': 'Column Break'
                },
                {
                    'label': 'Round Name',
                    'fieldname': 'round_name',
                    'fieldtype': 'Data',
                    'default': i['round'],
                    'read_only': 1
                },
                {
                    'label': 'Status',
                    'fieldname': 'status',
                    'fieldtype': 'Data',
                    'default': i['status'],
                    'read_only': 1
                },
                {
                    'label': '',
                    'fieldname': '',
                    'fieldtype': 'Column Break'
                },
                {
                    "label": "Interviewer's",
                    'fieldname': "interviewers",
                    "fieldtype": "Small Text",
                    "options": "Interviewer",
                    '_link_field':'employee',
                    'default': '\n'.join(l_),
                    'read_only': 1
                },
                {
                    "label": "Overall Recommendation",
                    'fieldname': "overall_recommendation",
                    "fieldtype": "Data",
                    'read_only': 1,
                    'default': i['overall_recommendation']
                },
                {
                    'label': '',
                    'fieldname': '',
                    'fieldtype': 'Section Break'

                }
            ]  
        list2.append(k)
        
        rounds_feedback = frappe.get_all('Interview Round Feedback', filters={'parent': i['name']}, fields=['*'])
        print(rounds_feedback, 'rounds feedback')
        if len(rounds_feedback) > 0:
            for i in rounds_feedback:
                l = [
                    {
                        'label': 'Skill',
                        'fieldname': 'skill',
                        'fieldtype': 'Link',
                        'read_only': 1,
                        'default': i['skill']
                    },
                    {
                        'label': '',
                        'fieldname': '',
                        'fieldtype': 'Column Break'
                    },
                    {
                        'label': 'Remark',
                        'fieldname': 'remark',
                        'fieldtype': 'Small Text',
                        'read_only': 1,
                        'default': i['remark']
                    },
                    {
                        'label': '',
                        'fieldname': '',
                        'fieldtype': 'Column Break'
                    },
                    {
                        'label': 'Rating',
                        'fieldname': 'rating',
                        'fieldtype': 'Int',
                        'read_only': 1,
                        'default': i['rating1']
                    },
                     
                    {
                        'label': '',
                        'fieldname': '',
                        'fieldtype': 'Section Break'
                    }

                ]
                list2.append(l)
        c = [
                {
                    'label': 'Comment',
                    'fieldname': 'comment',
                    'fieldtype': 'HTML Editor',
                    'read_only': 1,
                    'default': comment,
                    'Bold': 1
                    # 'default': a[0]['comment']
                },
                {
                    'label': '',
                    'fieldname': '',
                    'fieldtype': 'Section Break'
                }
            ]    
        list2.append(c)   
    interview_rounds = [val for sublist in list2 for val in sublist] 
    interviewer = frappe.get_doc('DocType', 'Interviewer')
    return {'interview_rounds': interview_rounds, 'interviewer': interviewer}

@frappe.whitelist()
def get_interview_and_interview_rounds(job_applicant, job_opening):
    interview = frappe.get_list("Interview", filters={'job_applicant': job_applicant}, fields=['*'])
    designation = frappe.get_list("Job Opening", filters={'name': job_opening}, fields=['designation'], as_list=1)
    print(designation)
    configuration = frappe.get_all('Interview Configuration', filters={'designation': designation[0][0]})
    print(len(configuration))
    if len(configuration) == 0:
        return False
    if len(interview) == 0:
        print("In if condition")
        rounds =  [
            {
                'label': 'Round 1',
                'fieldname': '',
                'fieldtype': 'Section Break'
            },

            {
                'label': 'Date',
                'fieldname': 'date',
                'fieldtype': 'Datetime'
            },
            {
                'label': '',
                'fieldname': '',
                'fieldtype': 'Column Break'
            },
            {
                    "label": "Interviewers",
                    'fieldname': "interviewers",
                    "fieldtype": "Table MultiSelect",
                    "options": "Interviewer",
                    '_link_field':'employee'
            }
        ] 
        interviewer = frappe.get_doc('DocType', 'Interviewer')
        return {'rounds':rounds, 'interviewer': interviewer}  
    else:
        print("in else condition")
        # created interview section
        list1 = []
        k = [
                {
                    'label': 'Interview',
                    'fieldname': 'interview',
                    'fieldtype': 'Link',
                    'options': 'Interview',
                    'default': interview[0]['name'],
                    'read_only': 1
                },
                {
                    'label': 'Job Opening',
                    'fieldname': 'job_opening',
                    'fieldtype': 'Link',
                    'options': 'Job Opening',
                    'default': interview[0]['job_opening'],
                    'read_only': 1
                },
                {
                    'label': '',
                    'fieldname': '',
                    'fieldtype': 'Column Break'
                },
                {
                    'label': 'Job Applicant',
                    'fieldname': 'job_applicant',
                    'fieldtype': 'Link',
                    'options': 'Job Applicant',
                    'default': interview[0]['job_applicant_name'],
                    'read_only': 1
                },
                {
                    'label': 'Designation',
                    'fieldname': 'designation',
                    'fieldtype': 'Link',
                    'options': 'Designation',
                    'default': interview[0]['designation'],
                    'read_only': 1
                }
        ]
        list1.append(k)
        interview_round = frappe.get_list('Interview Round', filters={'interview': interview[0]['name']}, fields=['*'], order_by = 'round_number')
        print(interview_round)
        for l in interview_round:
            
            interviewer = frappe.get_all('Interviewer', filters={'parent': l['name']}, fields=['employee', 'employee_name'] )
            l_ = []
            for row in interviewer:
                l_.append("{}-{}".format(row['employee'], row['employee_name']))
            #   created rounds section
            m =  [
                {
                    'label': 'Round' + ' ' + str(l['round_number']) + '-' + l['round'],
                    'fieldname': '',
                    'fieldtype': 'Section Break'
                },
                {
                    'label': 'Date',
                    'fieldname': 'date_',
                    'fieldtype': 'Datetime',
                    'default': l['date'],
                    'read_only': 1

                },
                {
                    'label': '',
                    'fieldname': '',
                    'fieldtype': 'Column Break'
                },
                {
                    "label": "Interviewers",
                    'fieldname': "interviewers",
                    "fieldtype": "Small Text",
                    "options": "Interviewer",
                    '_link_field':'employee',
                    'default': '\n'.join(l_),
                    'read_only': 1
                }
                
                ]
            list1.append(m)
        existing_rounds_ = frappe.get_list("Interview Round", fields=["round"], filters={
                                'interview': interview[0]['name']}, as_list=1)
        existing_rounds = [i[0] for i in existing_rounds_]
        # print(designation[0][0])
        rounds = frappe.get_list("Interview Round Configuration", fields=['*'], filters={'parent': interview[0]['designation'], 'round_name': ['not in', existing_rounds]}, order_by='round_number')
        if len(rounds) > 0:
            # new rounds section
            y =  [
                {
                    'label': 'Round' + ' ' + str(rounds[0]['round_number']) + '-' + rounds[0]['round_name'],
                    'fieldname': '',
                    'fieldtype': 'Section Break'
                },
                {
                    'label': 'Date',
                    'fieldname': 'date',
                    'fieldtype': 'Datetime',
                    # 'default': z['date']

                },
                {
                    'label': '',
                    'fieldname': '',
                    'fieldtype': 'Column Break'
                }, 
                {
                    "label": "Interviewers",
                    'fieldname': "interviewers",
                    "fieldtype": "Table MultiSelect",
                    "options": "Interviewer",
                    '_link_field':'employee'
                }
            ]
            list1.append(y)
        rounds_ = [val for sublist in list1 for val in sublist] 
        interviewer = frappe.get_doc('DocType', 'Interviewer')
        return {'rounds':rounds_, 'interviewer': interviewer} 

@frappe.whitelist()
def save_interview_round(formdata, job_applicant):
    data = json.loads(formdata)
  
    job_applicant_doc = frappe.get_doc("Job Applicant", job_applicant)

    job_opening_doc = frappe.get_doc("Job Opening", job_applicant_doc.job_title)

    get_interview = frappe.get_list('Interview', filters={'job_applicant': job_applicant}, as_list=1)

    job_opening = frappe.get_list('Job Opening', filters={'name' : job_opening_doc.name}, fields=['designation'], as_list =1)

    interview_configuration = frappe.get_list('Interview Round Configuration', filters={'parent': job_opening[0][0]}, fields=['round_number', 'round_name'], order_by='round_number')
    interview1 = frappe.get_list('Interview', filters={'job_applicant': job_applicant}, as_list=1)
    print(interview_configuration, len(interview_configuration))
    # configuration = frappe.get_all('Interview Configuration', filters={'designation': job_opening[0][0]})
    # print(len(configuration))
    # if len(configuration) == 0:
    #     return False

    if len(get_interview) == 0:
        interview = frappe.new_doc("Interview")
        interview.job_applicant = job_applicant
        interview.job_opening = job_opening_doc.name
        interview.designation = job_opening_doc.designation
        interview.current_round = interview_configuration[0]['round_name']
        interview.current_round_status = "Scheduled"
        interview.insert(ignore_permissions=True)
    
        interview1 = frappe.get_list('Interview', filters={'job_applicant': job_applicant}, as_list=1)
        interview_round = frappe.new_doc('Interview Round')
        interview_round.interview = interview1[0][0]
        interview_round.job_applicant = job_applicant
        interview_round.job_opening = job_opening_doc.name
        interview_round.designation = job_opening_doc.designation
        interview_round.attached_resume = job_applicant_doc.resume_attachment
        interview_round.round = interview_configuration[0]['round_name']
        interview_round.date = data['date']
        interview_round.round_number = interview_configuration[0]['round_number']
        # interview_round.interviewers = data['interviewers']
        for row in data['interviewers']:
            interview_round.append('interviewers', {
                'employee': row['employee']
            })
        interview_round.insert(ignore_permissions=True)

        job_applicant = frappe.get_doc('Job Applicant', job_applicant)
        job_applicant.current_round = 'Round' + " " + interview_configuration[0]['round_number']
        job_applicant.status = 'Round' + " " + interview_configuration[0]['round_number'] + " " + 'Scheduled'    
        job_applicant.save(ignore_permissions=True)
       
        print("Save interview round")

    else:
        existing_rounds_ = frappe.get_list("Interview Round", fields=["round"], filters={
                                'interview': interview1[0][0]}, as_list=1)
        existing_rounds = [i[0] for i in existing_rounds_]
        rounds = frappe.get_list("Interview Round Configuration", fields=['*'], filters={'parent': job_opening_doc.designation, 'round_name': ['not in', existing_rounds]}, order_by='round_number')
       
       
        interview = frappe.get_doc("Interview", get_interview[0][0])
        interview.current_round = rounds[0]['round_name']
        interview.current_round_status = "Scheduled"
        interview.save(ignore_permissions=True)

        interview_round = frappe.new_doc('Interview Round')
        interview_round.interview = get_interview[0][0]
        interview_round.job_applicant = job_applicant
        interview_round.job_opening = job_opening_doc.name
        interview_round.designation = job_opening_doc.designation
        interview_round.attached_resume = job_applicant_doc.resume_attachment
        interview_round.round = rounds[0]['round_name']
        interview_round.date = data['date']
        interview_round.round_number = rounds[0]['round_number']
        # interview_round.interviewers = data['interviewers']
        # interview_round.comments = 
        for row in data['interviewers']:
            interview_round.append('interviewers', {
                'employee': row['employee']
            })
        interview_round.insert(ignore_permissions=True)

        job_applicant = frappe.get_doc('Job Applicant', job_applicant)
        job_applicant.current_round = 'Round' + " " + rounds[0]['round_number']
        job_applicant.status = 'Round' + " " + rounds[0]['round_number'] + " " + 'Scheduled'    
        job_applicant.save(ignore_permissions=True)

def before_update_vehicle_log(doc, method):
    month = doc.date.split('-')	
    existing_vehicle_log = frappe.db.sql("""
                                select sum(todays_total_unit_consumed) from `tabVehicle Log` where month(date) = '{0}'
                            """.format(month[1]))
    frappe.db.set_value('Vehicle Log', {'name': doc.name}, 'monthly_units_consumed', existing_vehicle_log[0][0])

    if doc.service_required == 'Yes':
        frappe.db.set_value('Vehicle Log', {'name': doc.name}, 'total_running_hours', doc.todays_total_unit_consumed)
    else:
        a = frappe.db.get_all('Vehicle Log', {'name': ['!=', doc.name]}, ['total_running_hours', 'name'], order_by = 'name desc', page_length=1)
        if a:
            frappe.db.set_value('Vehicle Log', {'name': doc.name}, 'total_running_hours', doc.todays_total_unit_consumed + a[0]['total_running_hours'])
        else:
            frappe.db.set_value('Vehicle Log', {'name': doc.name}, 'total_running_hours', doc.todays_total_unit_consumed)
    frappe.db.commit()
    doc.reload()

def set_payeename(doc, method):
    if not doc.payee_name:
        print('=========================')
        print(doc.employee_name)
        frappe.db.set_value('Employee', {'name': doc.name}, 'payee_name', doc.employee_name) 
        frappe.db.commit()
        doc.reload()   