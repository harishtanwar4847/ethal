# -*- coding: utf-8 -*-
# Copyright (c) 2020, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import datetime

class WarningLetter(Document):
	
	def before_save(self):
		existing_warning_letter = frappe.db.get_all('Warning Letter', filters={'employee': self.employee, 'template': self.template}, fields=['*'])
		
		if existing_warning_letter:
			for i in existing_warning_letter:
				for warning_template in frappe.db.get_all('Warning Letter Template Details', filters={'parent': i['template'], 'frequency_of_offence': ['!=', i['frequency_of_offence']]}, fields=['*'], order_by='idx', limit=1):

					self.frequency_of_offence = warning_template['frequency_of_offence']
					self.type_of_warning = warning_template['type_of_warning']

					current_date_temp = datetime.datetime.strptime(frappe.utils.nowdate(), "%Y-%m-%d")
					newdate = current_date_temp + datetime.timedelta(days=warning_template['valid_for_days'])
					self.expiry_date = newdate
					print(newdate)
		else:
			for warning_template in frappe.db.get_all('Warning Letter Template Details', filters={'parent': self.template}, fields=['*'], order_by='idx', limit=1):
				self.frequency_of_offence = warning_template['frequency_of_offence']
				self.type_of_warning = warning_template['type_of_warning']

				current_date_temp = datetime.datetime.strptime(frappe.utils.nowdate(), "%Y-%m-%d")
				newdate = current_date_temp + datetime.timedelta(days=warning_template['valid_for_days'])
				self.expiry_date = newdate
			

def get_user():
	return frappe.get_all('Has Role', filters=[{'role': 'HR Manager'}, {'parenttype': 'User'}], fields=['parent'], as_list=1) 

@frappe.whitelist(allow_guest=True)
def set_warning_in_employee(employee, name):
	get_employee_warnings = frappe.get_all('Warning Letter Detail', filters={'parent': employee}, fields=['*'], order_by='idx desc', page_length=1)
	set_employee_warnings = frappe.get_doc('Employee', employee)
	# set_employee_warnings.append('warnings', {
	# 	'warning_letter': name
	# })
	set_employee_warnings.save()
	if not get_employee_warnings:
		set_employee_warnings.append('warnings', {
			'warning_letter': name
		})
		set_employee_warnings.warnings_status = 1
		set_employee_warnings.save(ignore_permissions=True)
	else:
		increase_warning_number = get_employee_warnings[0]['idx'] +1
		set_employee_warnings.append('warnings', {
			'warning_letter': name	
		})
		set_employee_warnings.warnings_status = increase_warning_number
		set_employee_warnings.save(ignore_permissions=True)
	frappe.db.commit()