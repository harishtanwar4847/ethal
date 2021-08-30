import frappe
from frappe.utils import getdate, nowdate, cint, flt
import json
from datetime import date, timedelta, datetime
import ast
import itertools
from erpnext.hr.doctype.employee_checkin.employee_checkin import mark_attendance_and_link_log
from frappe.utils.background_jobs import enqueue

def process_auto_attendance_for_holidays():
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