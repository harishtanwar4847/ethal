# Copyright (c) 2021, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class ShiftAssignmentBulk(Document):
	def before_insert(self):
		shift_assignment = frappe.db.sql("""
		select sabd.employee_name from `tabShift Assignment Bulk Detail` as sabd
		join `tabShift Assignment Bulk` sab
		on sabd.parent = sab.name
		where sab.date = '{}'
		""".format(self.date))

		content = "Shift Assignment already exist for this date of these employees"
		shift_assignments = ""
		if shift_assignment:
			for i in shift_assignment:
				shift_assignments += " " + frappe.bold(i[0])+ ", "  
		if len(shift_assignments) > 0:		
			frappe.throw(content+shift_assignments)

	def on_submit(self):
		employees = frappe.db.get_all('Shift Assignment Bulk Detail', filters={'parent': self.name}, fields=['employee', 'department', 'shift'])
		if employees:
			for employee in employees:
				shift_assignment = frappe.db.get_all('Shift Assignment', {'employee': employee['employee'], 'docstatus': 1}, ['name'], order_by='name desc', limit=1)
				if shift_assignment:
					existing_shift_assignment = frappe.get_doc('Shift Assignment', shift_assignment[0]['name'])
					shift_date = datetime.strptime(self.date, '%Y-%m-%d')
					subtract_day = timedelta(days=1)
					existing_shift_assignment.end_date = shift_date - subtract_day
					existing_shift_assignment.save()

				create_shift_assignment = frappe.new_doc('Shift Assignment')
				create_shift_assignment.employee = employee['employee']
				create_shift_assignment.start_date = self.date
				create_shift_assignment.shift_bulk_assignment = self.name
				create_shift_assignment.shift_type = employee['shift']
				create_shift_assignment.department = employee['department']
				create_shift_assignment.submit()	
			
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
					distinct t1.name as employee, t1.employee_name, t1.department, t1.designation, t1.working_area
				from
					`tabEmployee` t1
				where t1.status = 'Active' %s
			""" % cond,  as_dict=True)
			
		else:
			emp_list = frappe.db.sql("""
				select
					distinct t1.name as employee, t1.employee_name, t1.department, t1.designation, t1.working_area
				from
					`tabEmployee` t1
			""",  as_dict=True)
		for i in emp_list:
			previous_shift = frappe.db.get_all('Shift Assignment', {'employee': i['employee']}, ['shift_type'], order_by='name desc', limit=1)
			i['previous_shift'] = previous_shift[0]['shift_type'] if previous_shift else None
		
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
		for f in ['company', 'branch', 'department', 'designation', 'working_area']:
			if self.get(f):
				cond += "and t1." + f + " = '" + self.get(f).replace("'", "\'") + "'"
		return cond
