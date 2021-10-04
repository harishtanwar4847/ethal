# -*- coding: utf-8 -*-
# Copyright (c) 2020, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import datetime

class WarningLetter(Document):
	
	def validate(self):
		self.issue_date = frappe.utils.nowdate() if not self.issue_date else self.issue_date
		existing_warning_letter = frappe.db.get_all('Warning Letter', filters={'employee': self.employee, 'template': self.template, 'name': ['!=', self.name], 'docstatus': ['<', 2]}, fields=['*'], order_by='name desc')	
		if existing_warning_letter:
			freuquency = []
			for i in existing_warning_letter:
				freuquency.append(i['frequency_of_offence'])

			for warning_template in frappe.db.get_all('Warning Letter Template Details', filters={'parent': self.template, 'frequency_of_offence': ('not in', freuquency)}, fields=['*'], order_by = 'idx asc', limit=1):
				
				self.frequency_of_offence = warning_template['frequency_of_offence']
				self.type_of_warning = warning_template['type_of_warning']
				
				current_date_temp = datetime.datetime.strptime(self.issue_date, "%d-%m-%Y")
				newdate = current_date_temp + datetime.timedelta(days=warning_template['valid_for_days'])
				self.expiry_date = newdate
		
		else:
			for warning_template in frappe.db.get_all('Warning Letter Template Details', filters={'parent': self.template}, fields=['*'], order_by='idx', limit=1):
				self.frequency_of_offence = warning_template['frequency_of_offence']
				self.type_of_warning = warning_template['type_of_warning']
				current_date_temp = datetime.datetime.strptime(self.issue_date, "%d-%m-%Y")
				newdate = current_date_temp + datetime.timedelta(days=warning_template['valid_for_days'])
				self.expiry_date = newdate	

	def on_submit(self):
		get_employee_warnings = frappe.get_all('Warning Letter Detail', filters={'parent': self.employee}, fields=['*'], order_by='idx desc', page_length=1)
		set_employee_warnings = frappe.get_doc('Employee', self.employee)
		if not get_employee_warnings:
			set_employee_warnings.append('warnings', {
				'warning_letter': self.name
			})
			set_employee_warnings.warnings_status = 1
			set_employee_warnings.save(ignore_permissions=True)
		else:
			increase_warning_number = get_employee_warnings[0]['idx'] +1
			set_employee_warnings.append('warnings', {
				'warning_letter': self.name	
			})
			set_employee_warnings.warnings_status = increase_warning_number
			set_employee_warnings.save(ignore_permissions=True)
		frappe.db.commit() 	

def get_user():
	return frappe.get_all('Has Role', filters=[{'role': 'HR Manager'}, {'parenttype': 'User'}], fields=['parent'], as_list=1) 

