import frappe
from frappe.utils import getdate, nowdate, cint, flt
import json
from datetime import date, timedelta, datetime
import ast
import itertools
from erpnext.hr.doctype.employee_checkin.employee_checkin import mark_attendance_and_link_log
from frappe.utils.background_jobs import enqueue

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

def shift_rotate():
    print("rotate shift method call")
    female_employee = frappe.db.get_all('Employee', filters = {'gender': 'Female', 'shift_rotate': 1}, fields=['name'], as_list=1)
    if female_employee:
        female_employee_store_in_list = [i[0] for i in female_employee]
        female_employee_convert_tuple = tuple(female_employee_store_in_list)
        frappe.db.sql("""
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
        frappe.db.sql("""
                       Update `tabEmployee`
                       SET default_shift = CASE 
                       WHEN default_shift='A' THEN 'B' 
                       WHEN default_shift='B' THEN 'C' 
                       WHEN default_shift='C' THEN 'A' 
                       ELSE default_shift END where employee in {}; 
                    """.format(male_employee_convert_tuple))
        frappe.db.commit()

@frappe.whitelist()
def calculate_overtime_in_salary_slip(doc, method):
    daily_overtime(doc)
    process_auto_attendance_for_holidays(doc)

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
    shift = frappe.db.get_value('Employee', {'employee': doc.employee, 'is_overtime_applicable': 1}, ['default_shift'])
    if shift:   
        attendances = frappe.db.get_all('Attendance', filters=filters, fields=['working_hours'])
        if attendances:
            doc.sunday_ot_hours = attendances[0].working_hours

def holiday_overtime(doc):
    sunday = frappe.db.get_all('Holiday', filters={'description': 'Sunday', 'holiday_date': ('between',[ doc.start_date, doc.end_date])},  fields=['holiday_date'], as_list=1)
    sunday_ = []
    for i in sunday:
        splitsundaydate = i[0].strftime('%Y-%m-%d')
        sunday_.append(splitsundaydate)
    
    holiday = frappe.db.get_all('Holiday', filters={'holiday_date': ['not in', sunday_]},  fields=['holiday_date'], as_list=1)
    holiday_ = []
    for i in holiday:
        splitholidaydate = i[0].strftime('%Y-%m-%d')
        holiday_.append(splitholidaydate)
    
    filters = [
        ['employee', '=', doc.employee],
        ['attendance_date', 'in', holiday_]
    ]
    shift = frappe.db.get_value('Employee', {'employee': doc.employee, 'is_overtime_applicable': 1}, ['default_shift'])
    if shift:   
        attendances = frappe.db.get_all('Attendance', filters=filters, fields=['working_hours'])
        if attendances:
            doc.holiday_ot_hours = attendances[0].working_hours

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

def before_submit_stock_entry(doc, method):
    if doc.value_difference > 1:
        frappe.throw('Incoming Value not equal to Outgoing Value! Please Correct the rate.')

def on_update_employee(doc, method):
    get_salary_structure_ass = frappe.get_all('Salary Structure Assignment', filters={'employee': doc.employee, 'docstatus': 1})
    print('ja na be')
    if get_salary_structure_ass:
        frappe.db.set_value('Salary Structure Assignment', {'name': get_salary_structure_ass[0].name}, 'salary_structure', doc.grade)
        employee_grade = frappe.db.get_value('Employee Grade', doc.grade, 'base_amount')
        frappe.db.set_value('Salary Structure Assignment', {'name': get_salary_structure_ass[0].name}, 'base', employee_grade)
        frappe.db.set_value('Salary Structure Assignment', {'name': get_salary_structure_ass[0].name}, 'salary_in_usd', employee_grade)
        frappe.db.set_value('Salary Structure Assignment', {'name': get_salary_structure_ass[0].name}, 'staus', 'Salary Updated')
        frappe.db.commit()

def trigger_mail_if_absent_consecutive_5_days(doc, method):

    attendance = frappe.db.sql("""
    select count(attendance_date) as count
    from `tabAttendance` 
    where  attendance_date >= DATE_SUB(CURDATE(), INTERVAL 5 DAY) 
    and status='Absent' and employee='{}' order by attendance_date;

    """.format(doc.employee), as_dict = 1)

    if attendance[0]['count'] == 5:
        notification = frappe.get_doc('Notification', 'Consecutive Leave')

        args={'doc': doc}
        recipients = notification.get_list_of_recipients(doc, args)
        print(recipients)
        recipients_list = list(recipients[0])
        message = 'Alert! {} has been on Leave for 5 consecutive days.'.format(doc.employee_name)
        for user in recipients_list:
            frappe.publish_realtime(event='msgprint',message=message,user=user)
        frappe.enqueue(method=frappe.sendmail, recipients=recipients, sender=None, now=True,
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
        