import frappe
from frappe.utils import getdate, nowdate, cint, flt
import json
from datetime import date, timedelta, datetime
import time
from frappe.utils import formatdate
import ast
from frappe.utils import get_url_to_form
import itertools
from erpnext.hr.doctype.employee_checkin.employee_checkin import mark_attendance_and_link_log
from frappe.utils.background_jobs import enqueue

@frappe.whitelist()
def set_approver_name(doc, method):
	doc.approver_person = doc.modified_by
	doc.approver_date = doc.modified

	get_approver_name = frappe.db.get_value('Comment', {'reference_name':doc.name, 'content': 'Sent for Approval'}, 'owner')
	print(get_approver_name)
	get_approved_date = frappe.db.get_value('Comment', {'reference_name':doc.name, 'content': 'Sent for Approval'}, 'modified')
	print(get_approved_date)
	frappe.db.set_value(doc.doctype, {'name': doc.name}, 'checked_person', get_approver_name)
	frappe.db.set_value(doc.doctype, {'name': doc.name}, 'checked_date', get_approved_date)


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

def set_payeename(doc, method):
	if not doc.payee_name:
		frappe.db.set_value('Customer', {'name': doc.name}, 'payee_name', doc.customer_name)
		frappe.db.commit()
		doc.reload()

def supplier_set_payeename(doc, method):
	if not doc.payee_name:
		frappe.db.set_value('Supplier', {'name': doc.name}, 'payee_name', doc.supplier_name)
		frappe.db.commit()
		doc.reload()

def shareholder_set_payeename(doc, method):
	if not doc.payee_name:
		frappe.db.set_value('Shareholder', {'name': doc.name}, 'payee_name', doc.title)
		frappe.db.commit()
		doc.reload()	

def send_api_message(doc, method):
	doc_link = get_url_to_form(doc.doctype, doc.name)

	message = 'Test - {} {} has been submitted. Please check it out. {}'.format(doc.doctype, doc.name, doc_link)

	telegram_bot_settings = frappe.get_doc('Telegram Bot Settings')
	
	if doc.doctype == 'Delivery Note':
		telegram_bot_settings.send_telegram_message(message, 'Sales')
	elif doc.doctype == 'Purchase Receipt':
		telegram_bot_settings.send_telegram_message(message, 'Stock')	
	elif doc.doctype == 'Material Request':
		telegram_bot_settings.send_telegram_message(message, 'Purchase')		