# -*- coding: utf-8 -*-
# Copyright (c) 2020, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class WarningLetter(Document):
	pass


def get_user():
	return frappe.get_all('Has Role', filters=[{'role': 'HR Manager'}, {'parenttype': 'User'}], fields=['parent'], as_list=1) 

@frappe.whitelist(allow_guest=True)
def set_warning(employee):
	
	get_employee_warnings = frappe.get_all('Warning Letter Detail', filters={'parent': employee}, fields=['warning_number'], order_by='warning_number desc', page_length=1)
	print('get employees', get_employee_warnings)
	if not get_employee_warnings:
		return 1
	elif get_employee_warnings[0]['warning_number'] == 3:
		recipients_list = get_user()
		message = 'ja na be'
		for user in recipients_list:
			frappe.publish_realtime(event='msgprint',message=message,user=user[0])
			frappe.throw('ja na be')
	else:
		print(get_employee_warnings)
		increase_warning_number = get_employee_warnings[0]['warning_number']
		increase_warning_number = increase_warning_number+1
		return increase_warning_number

@frappe.whitelist(allow_guest=True)
def set_warning_in_employee(employee, name):
	get_employee_warnings = frappe.get_all('Warning Letter Detail', filters={'parent': employee}, fields=['warning_number'], order_by='warning_number desc', page_length=1)
	set_employee_warnings = frappe.get_doc('Employee', employee)
	if not get_employee_warnings:
		set_employee_warnings.append('warnings', {
			'warning_letter': name
		})
		set_employee_warnings.warnings_status = 1
		set_employee_warnings.save(ignore_permissions=True)
	else:
		if get_employee_warnings[0]['warning_number'] == 2:
			recipients_list = get_user()
			message = 'ja na be'
			for user in recipients_list:
				frappe.publish_realtime(event='msgprint',message=message,user=user[0])
		increase_warning_number = get_employee_warnings[0]['warning_number'] +1
		set_employee_warnings.append('warnings', {
			'warning_letter': name
		})
		set_employee_warnings.warnings_status = increase_warning_number
		set_employee_warnings.save(ignore_permissions=True)
	frappe.db.commit()