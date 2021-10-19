# Copyright (c) 2021, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
import datetime
from dateutil.relativedelta import relativedelta

class EmployeeCashIncentiveBulk(Document):
	def get_emp_list(self):
		"""
			Returns list of active employees based on selected criteria
			and for which salary structure exists
		"""

		cond = self.get_filter_condition()
		# cond += self.get_joining_relieving_condition()
		if cond:
			emp_list = frappe.db.sql("""
				select
					distinct t1.name as employee, t1.employee_name, t1.department, t1.designation
				from
					`tabEmployee` t1
				where t1.status = 'Active' %s
			""" % cond,  as_dict=True)
			print(emp_list)
		else:
			emp_list = frappe.db.sql("""
				select
					distinct t1.name as employee, t1.employee_name, t1.department, t1.designation
				from
					`tabEmployee` t1
			""",  as_dict=True)
			print(emp_list)	
		return emp_list

	@frappe.whitelist()
	def fill_employee_details(self):
		
		self.set('employee_details', [])
		employees = self.get_emp_list()
		if not employees:
			frappe.throw(_("No employees for the mentioned criteria"))
			
		for d in employees:
			self.append('employee_details', d)

		self.number_of_employees = len(employees)
		# if self.validate_attendance:
		# return self.validate_employee_attendance()

	def get_filter_condition(self):
		# self.check_mandatory()

		cond = ''
		for f in ['company', 'branch', 'department', 'designation']:
			if self.get(f):
				cond += "and t1." + f + " = '" + self.get(f).replace("'", "\'") + "'"
		return cond

