import frappe
from frappe.utils import getdate, nowdate, cint, flt
import json
from datetime import date, timedelta, datetime
import ast
import itertools
from erpnext.hr.doctype.employee_checkin.employee_checkin import mark_attendance_and_link_log
from frappe.utils.background_jobs import enqueue

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
    admin_settings = frappe.get_doc('Admin Settings')
    admin_settings_document = frappe.get_all('Admin Settings Document', {'parent': 'Admin Settings', 'document': doc.doctype}, ['posting_date'], as_list=1)  
    if admin_settings_document:
        if admin_settings.closure_date > doc.posting_date:
            frappe.throw('please contact manager')

@frappe.whitelist()
def set_approver_name(data):
    data=json.loads(data)
    
    get_approver_name = frappe.db.get_value('Comment', {'reference_name':data['name'], 'content': 'Approved'}, 'owner')
    
    get_approved_date = frappe.db.get_value('Comment', {'reference_name':data['name'], 'content': 'Approved'}, 'modified')
    
    frappe.db.set_value(data['doctype'], {'name': data['name']}, 'approver_person', get_approver_name)
    frappe.db.set_value(data['doctype'], {'name': data['name']}, 'approver_date', get_approved_date)
    frappe.db.commit()