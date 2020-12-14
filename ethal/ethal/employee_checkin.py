import frappe
from frappe.utils import getdate, nowdate, cint, flt
import json
from datetime import date, timedelta, datetime
import ast
import itertools
from erpnext.hr.doctype.employee_checkin.employee_checkin import mark_attendance_and_link_log
from frappe.utils.background_jobs import enqueue

@frappe.whitelist()
def calculate_overtime_in_salary_slip(doc, method):
    print("hello")
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
    print('ja na be')
    holiday = frappe.db.get_all('Holiday', filters={'description': 'Sunday', 'holiday_date': ('between',[ doc.start_date, doc.end_date])},  fields=['holiday_date'], as_list=1)
    print(holiday)
    holiday_ = []
    for i in holiday:
        splitdate = i[0].strftime('%Y-%m-%d')
        holiday_.append(splitdate)
  
    filters = [
        ['employee', '=', doc.employee],
        ['attendance_date', 'in', holiday_]
    ]
    shift = frappe.db.get_value('Employee', {'employee': doc.employee, 'is_overtime_applicable': 1}, ['default_shift'])
    print(shift)
    if shift:   
        attendances = frappe.db.get_all('Attendance', filters=filters, fields=['working_hours'])
        print(attendances)
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
