import frappe
from frappe.utils import getdate, nowdate, cint, flt
import json
from datetime import date, timedelta, datetime
from frappe.utils import formatdate
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

@frappe.whitelist()
def set_approver_name(data):
    data=json.loads(data)
    
    get_approver_name = frappe.db.get_value('Comment', {'reference_name':data['name'], 'content': 'Approved'}, 'owner')
    
    get_approved_date = frappe.db.get_value('Comment', {'reference_name':data['name'], 'content': 'Approved'}, 'modified')
    
    frappe.db.set_value(data['doctype'], {'name': data['name']}, 'approver_person', get_approver_name)
    frappe.db.set_value(data['doctype'], {'name': data['name']}, 'approver_date', get_approved_date)
    frappe.db.commit()

@frappe.whitelist()
def before_insert_payment_entry(doc, method):
    if doc.naming_series.startswith('CPV'):
        payment_entries = frappe.db.get_value('Payment Entry', {'reference_no': doc.reference_no}, ['name'])
        if payment_entries:
            frappe.throw('Cheque/Reference no must be unique')   