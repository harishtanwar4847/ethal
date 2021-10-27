# Copyright (c) 2021, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
import datetime
from dateutil.relativedelta import relativedelta

class ShiftAssignmentBulk(Document):
	def on_submit(self):
		employees = frappe.db.get_all('Shift Assignment Bulk Detail', filters={'parent': self.name}, fields=['employee', 'department'])
		if employees:
			a = 'Employees already have Active Shift '
			shift_assignments = ''
			print(len(shift_assignments))	
			for employee in employees:
				shift_assignment = frappe.db.get_value('Shift Assignment', {'employee': employee['employee'], 'start_date': ['=', self.date], 'docstatus': 1}, ['name'])
				print(shift_assignment)
				if shift_assignment:
					shift_assignments += frappe.bold(shift_assignment)+ ' '
				else:
					create_shift_assignment = frappe.new_doc('Shift Assignment')
					create_shift_assignment.employee = employee['employee']
					create_shift_assignment.start_date = self.date
					# create_shift_assignment.end_date = self.date
					create_shift_assignment.shift_bulk_assignment = self.name
					create_shift_assignment.shift_type = self.shift
					create_shift_assignment.department = employee['department']
					create_shift_assignment.submit()	
			if len(shift_assignments) > 0:
				frappe.msgprint(a+shift_assignments)	

	def on_cancel(self):
		frappe.delete_doc("Shift Assignment", frappe.db.sql_list("""select name from `tabShift Assignment`
			where shift_bulk_assignment=%s """, (self.name)))

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
