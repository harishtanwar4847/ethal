import frappe
from frappe.utils import getdate, nowdate, cint, flt
import json
from datetime import date, timedelta, datetime
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
def before_save_asset_maintenance_log(doc, method):  
    asset_maintenance_task = frappe.get_all('Asset Maintenance Task', filters={'parent': doc.asset_maintenance}, fields=['maintanence_category', 'maintenance_task'])
    if asset_maintenance_task:
        for row in asset_maintenance_task:
            print(row['maintenance_task'])
            frappe.db.set_value('Asset Maintenance Log', {'task_name': row['maintenance_task']}, 'maintanence_category', row['maintanence_category'])

@frappe.whitelist()
def create_stock_entry(doc, method):
    get_part_used = frappe.get_all('Parts Used Item Table', filters = {'parent': doc.name}, fields=['*'])
    print(get_part_used)
    stock_entry = frappe.new_doc('Stock Entry')
    stock_entry.stock_entry_type= 'Material Issue'
    for row in get_part_used:
        source_warehouse = frappe.db.get_all('Item Default', {'parent': row['item']}, ['default_warehouse'])
        stock_entry.append('items', {
            's_warehouse': source_warehouse[0].default_warehouse,
            'item_code': row['item'],
            'item_group': row['item_group'],
            'qty': row['quantity'],
            'uom': row['uom']
        })
        stock_entry.insert(ignore_permissions=True)
        stock_entry.docstatus = 1

@frappe.whitelist()
def create_stock_entry_from_asset_repair(doc, method):
    get_part_used = frappe.get_all('Parts Used Item Table', filters = {'parent': doc.name}, fields=['*'])
    print(get_part_used)
    stock_entry = frappe.new_doc('Stock Entry')
    stock_entry.stock_entry_type= 'Material Issue'
    for row in get_part_used:
        source_warehouse = frappe.db.get_all('Item Default', {'parent': row['item']}, ['default_warehouse'])
        stock_entry.append('items', {
            's_warehouse': source_warehouse[0].default_warehouse,
            'item_code': row['item'],
            'item_group': row['item_group'],
            'qty': row['quantity'],
            'uom': row['uom']
        })
    stock_entry.insert(ignore_permissions=True)
    stock_entry.docstatus = 1

@frappe.whitelist()
def before_submit_leave_allocation(doc, method):
    doj = frappe.db.get_value('Employee', doc.employee, 'date_of_joining')
    today = frappe.db.get_value('Leave Allocation', doc.name, 'from_date')
    total_experience = today.year - doj.year - ((today.month, today.day) < (doj.month, doj.day)) + 1
    get_total_leaves = convert_year_to_leaves(total_experience)
    frappe.db.set_value('Leave Allocation', doc.name, 'new_leaves_allocated', get_total_leaves)
    frappe.db.set_value('Leave Allocation', doc.name, 'total_leaves_allocated', get_total_leaves)
   
def convert_year_to_leaves(year):
    leaves = ((year-1)/2)+16 
    return leaves

@frappe.whitelist()
def set_items_from_stock_entry(name):
    stock_entry_detail = frappe.get_all('Stock Entry Detail', filters={'parent': name}, fields=['*'])
    for i in stock_entry_detail:
        return i

@frappe.whitelist()
def before_submit_all_doctypes(doc, method):
    user = frappe.get_roles(frappe.session.user)
    admin_settings = frappe.get_doc('Admin Settings')
    admin_settings_document = frappe.get_all('Admin Settings Document', {'parent': 'Admin Settings', 'document': doc.doctype}, ['date'], as_list=1)  
   
    if admin_settings.applicable_for_role not in user:
        if admin_settings_document:
            if admin_settings_document[0][0] == 'posting_date':
                if admin_settings.closure_date > doc.posting_date:
                    frappe.throw(frappe._("You are not authorized to add or update entries before {0}").format(formatdate(admin_settings.closure_date)))
            elif admin_settings_document[0][0] == 'transaction_date':
                if admin_settings.closure_date > doc.transaction_date:
                    frappe.throw(frappe._("You are not authorized to add or update entries before {0}").format(formatdate(admin_settings.closure_date)))

def shift_rotate():
    print("rotate shift method call")
    female_employee = frappe.db.get_all('Employee', filters = {'gender': 'Female', 'shift_rotate': 1}, fields=['name'], as_list=1)
    if female_employee:
        female_employee_store_in_list = [i[0] for i in female_employee]
        female_employee_convert_tuple = tuple(female_employee_store_in_list)
        rotate_shift = frappe.db.sql("""
                            Update `tabEmployee` 
                            SET default_shift = CASE 
                            WHEN default_shift='A' THEN 'B' 
                            WHEN default_shift='B' THEN 'A' 
                            ELSE default_shift END where employee in {}; 
                        """.format(female_employee_convert_tuple))
        frappe.db.commit()

    male_employee = frappe.db.get_all('Employee', filters = {'gender': 'Male','shift_rotate': 1}, fields=['name'], as_list=1)
    if male_employee:
        male_employee_store_in_list = [i[0] for i in male_employee]
        male_employee_convert_tuple = tuple(male_employee_store_in_list)
        rotate_shift = frappe.db.sql("""
                        Update `tabEmployee`
                        SET default_shift = CASE 
                        WHEN default_shift='A' THEN 'B' 
                        WHEN default_shift='B' THEN 'C' 
                        WHEN default_shift='C' THEN 'A' 
                        ELSE default_shift END where employee in {}; 
                        """.format(male_employee_convert_tuple)); 
        frappe.db.commit()

@frappe.whitelist()
def set_approver_name(doc, method):
    doc.approver_person = doc.modified_by
    doc.approver_date = doc.modified

@frappe.whitelist()
def calculate_overtime_in_salary_slip(doc, method):
    daily_overtime(doc)
    sunday_overtime(doc)
    holiday_overtime(doc)
    # process_auto_attendance_for_holidays(doc)

def daily_overtime(doc):
    filters = [
        ['employee', '=', doc.employee],
        ['attendance_date', '<=', doc.end_date],
        ['attendance_date', '>=', doc.start_date]
    ]
    filters_checkout = [
        ['employee', '=', doc.employee],
        ['shift_end', '<=', doc.end_date],
        ['shift_end', '>=', doc.start_date],
        ['log_type','=','OUT']
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
            i = int(i)
            if i > shift_time and i < 15:
                doc.normal_ot_hours = doc.normal_ot_hours + (i - shift_time)

        midnight_checkout = frappe.db.get_all('Employee Checkin', filters=filters_checkout, fields=['time'], as_list=True)

        for i in midnight_checkout:
            for j in i:
                if j.hour== 23 and j.minute == 59 and j.second == 59:
                    doc.normal_ot_hours = doc.normal_ot_hours + 1

def sunday_overtime(doc):
   
    holiday = frappe.db.get_all('Holiday', filters={'description': 'Sunday', 'holiday_date': ('between',[ doc.start_date, doc.end_date])},  fields=['holiday_date'], as_list=1)
   
    holiday_ = []
    for i in holiday:
        splitdate = i[0].strftime('%Y-%m-%d')
        holiday_.append(splitdate)
  
    filters = [
        ['employee', '=', doc.employee],
        ['attendance_date', 'in', holiday_]
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
        ['attendance_date', 'in', holiday_]
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

@frappe.whitelist()
def before_insert_salary_structure_assignment(doc, method):
    get_employee_base_amount = frappe.db.get_value('Employee Grade', {'default_salary_structure': doc.salary_structure}, 'base_amount')
    frappe.db.set_value('Salary Structure Assignment', {'name': doc.name}, 'base', get_employee_base_amount)
    frappe.db.commit()

def process_auto_attendance_for_holidays(doc):
    # sauce: shift_type.py
    # get employee checkins that don't have shifts and don't have marked attendances
    # filters dict defines employee checkin on holiday
    filters = {
        'skip_auto_attendance': '0',
        'attendance': ('is', 'not set'),
        'shift': ('is', 'not set')
    }
    logs = frappe.db.get_list(
        'Employee Checkin', fields="*", filters=filters, order_by="employee,time")
    print("logs ========>", logs)
   
    # process employee checkins on holiday
    for key, group in itertools.groupby(logs, key=lambda x: (x['employee'], x['time'].strftime('%Y-%m-%d'))):
        # get default shift from employee for the date on which employee checkin is marked
        shift_for_the_day = frappe.db.get_value(
            'Employee', key[0], 'default_shift')
        print("key =======>", key)
        print("group ========>", group)
        # mark attendance only if shift is assigned on the said date
        if shift_for_the_day:
            shift = frappe.get_doc('Shift Type', shift_for_the_day)
            single_shift_logs = list(group)
            attendance_status, working_hours, late_entry, early_exit = shift.get_attendance(
                single_shift_logs)
            mark_attendance_and_link_log(
                single_shift_logs, attendance_status, key[1], working_hours, late_entry, early_exit, shift.name)

    frappe.db.commit()
    sunday_overtime(doc)
    holiday_overtime(doc)

@frappe.whitelist()
def before_submit_stock_entry(doc, method):
    if doc.value_difference > 1:
        frappe.throw('Incoming Value not equal to Outgoing Value! Please Correct the rate.')

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

@frappe.whitelist()
def set_conversion_rate(employee):
    employee_list = frappe.db.get_all('Payroll Employee Detail', {'employee': employee}, ['parent'], order_by='creation desc', limit=1, as_list=1)
    if employee_list:
        get_conversion_rate = frappe.db.get_value('Payroll Entry', employee_list[0][0], 'conversion_rate')
        return get_conversion_rate
        
@frappe.whitelist()
def assign_salary_structure(doc, company=None, grade=None, department=None, designation=None,employee=None,
        from_date=None, base=None, variable=None, income_tax_slab=None):
    employees = get_employees(doc, company= company, grade= grade,department= department,designation= designation,name=employee)

    if employees:
        if len(employees) > 20:
            frappe.enqueue(assign_salary_structure_for_employees, timeout=600,
                employees=employees, salary_structure=doc,from_date=from_date,
                base=base, variable=variable, income_tax_slab=income_tax_slab)
        else:
            assign_salary_structure_for_employees(employees, doc, from_date=from_date,
                base=base, variable=variable, income_tax_slab=income_tax_slab)
    else:
        frappe.msgprint(frappe._("No Employee Found"))

def before_insert_salary_structure_assignment(doc, method):
    get_employee_base_amount = frappe.db.get_value('Employee Grade', {'default_salary_structure': doc.salary_structure}, 'base_amount')
    set_base_amount_in_salary_structure_ass = frappe.db.set_value('Salary Structure Assignment', {'name': doc.name}, 'base', get_employee_base_amount)
    frappe.db.commit()

def assign_salary_structure_for_employees(employees, salary_structure, from_date=None, base=None, variable=None, income_tax_slab=None):
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
def make_salary_slip(source_name, target_doc = None, employee = None, as_print = False, print_format = None, for_preview=0, ignore_permissions=False):
	def postprocess(source, target):
		if employee:
			employee_details = frappe.db.get_value("Employee", employee,
				["employee_name", "branch", "designation", "department"], as_dict=1)
			target.employee = employee
			target.employee_name = employee_details.employee_name
			target.branch = employee_details.branch
			target.designation = employee_details.designation
			target.department = employee_details.department
		target.run_method('process_salary_structure', for_preview=for_preview)

	doc = get_mapped_doc("Salary Structure", source_name, {
		"Salary Structure": {
			"doctype": "Salary Slip",
			"field_map": {
				"total_earning": "gross_pay",
				"name": "salary_structure"
			}
		}
	}, target_doc, postprocess, ignore_child_tables=True, ignore_permissions=ignore_permissions)

	if cint(as_print):
		doc.name = 'Preview for {0}'.format(employee)
		return frappe.get_print(doc.doctype, doc.name, doc = doc, print_format = print_format)
	else:
		return doc



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

@frappe.whitelist()
def before_insert_payment_entry(doc, method):
    if doc.naming_series.startswith('CPV') and doc.mode_of_payment == 'Cheque':
        payment_entries = frappe.db.get_value('Payment Entry', {'reference_no': doc.reference_no, 'docstatus': ['!=', '2']}, ['name'])
        if payment_entries == None:
            return
        elif payment_entries != doc.name:    
            frappe.throw('Cheque/Reference no must be unique')   

def before_insert_sales_invoice(doc, method):
    if doc.naming_series.startswith('ACSI-TU'):
        sales_invoice = frappe.db.get_value('Sales Invoice', {'fs_number': doc.fs_number, 'naming_series': ['like', '%ACSI-TU-%'], 'docstatus': ['!=', '2']}, ['name'])
        if sales_invoice == None:
            return
        elif sales_invoice != doc.name:    
            frappe.throw('FS Numer must be unique')   
    elif doc.naming_series.startswith('ACSI-DB'):  
        sales_invoice = frappe.db.get_value('Sales Invoice', {'fs_number': doc.fs_number, 'naming_series': ['like', '%ACSI-DB-%'], 'docstatus': ['!=', '2']}, ['name'])
        if sales_invoice == None:
            return
        elif sales_invoice != doc.name:    
            frappe.throw('FS Numer must be unique')   