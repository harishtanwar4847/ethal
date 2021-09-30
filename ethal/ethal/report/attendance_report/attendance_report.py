# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns, data = [], []
	columns = ['Employee:Link/Employee:200']+['Employee Name:Data:250']+['Attendance Date:Date:150']+['Status:Data:200']+['Department:Link/Department:200']+['Shift:Link/Shift Type:150']+['Working Hours:Float:150']+['OT:Float:150']+['Incentive:Float:150']
	data = get_data(filters)
	return columns, data

def get_data(filters):
	if 'department' in filters and not 'shift' in filters:
		query = frappe.db.sql("""
		select employee, employee_name, attendance_date, status, department, shift, working_hours 
		from `tabAttendance`
		where status = '{}'
		and attendance_date between '{}' and '{}'
		and department = '{}'
		""".format(filters['status'], filters['from_date'], filters['to_date'], filters['department']), as_dict=1)
		if query:
			for i in query:
				shift = 0
				shift_start = frappe.db.get_value('Shift Type',i['shift'],'start_time')
				shift_end = frappe.db.get_value('Shift Type',i['shift'],'end_time')
				if shift_end is not None and shift_start is not None:
					shift_time = shift_end - shift_start
					hours = shift_time.seconds
					total = hours//3600
					if i['working_hours'] > total:
						shift = i['working_hours'] - total
				i['ot'] = shift
				employee_incentive = frappe.db.sql("""
						select coalesce(sum(eibd.incentive_hours), 0) from `tabEmployee Incentive Bulk Detail` as eibd 
						join `tabEmployee Incentive Bulk` as eib on eibd.parent = eib.name
						where eib.incentive_date = '{0}'
						and eibd.employee = '{1}' and eib.salary_component = 'Production Incentive' and eib.docstatus = 1
				""".format(i['attendance_date'], i['employee']))
				i['incentive'] = employee_incentive[0][0]		
			return query
	elif 'department' in filters and 'shift' in filters:
		query = frappe.db.sql("""
		select employee, employee_name, attendance_date, status, department, shift, working_hours 
		from `tabAttendance`
		where status = '{}'
		and attendance_date between '{}' and '{}'
		and department = '{}' and shift = '{}'
		""".format(filters['status'], filters['from_date'], filters['to_date'], filters['department'], filters['shift']), as_dict=1)
		if query:
			for i in query:
				shift = 0
				shift_start = frappe.db.get_value('Shift Type',i['shift'],'start_time')
				shift_end = frappe.db.get_value('Shift Type',i['shift'],'end_time')
				if shift_end is not None and shift_start is not None:
					shift_time = shift_end - shift_start
					hours = shift_time.seconds
					total = hours//3600
					if i['working_hours'] > total:
						shift = i['working_hours'] - total
				i['ot'] = shift
				employee_incentive = frappe.db.sql("""
						select coalesce(sum(eibd.incentive_hours), 0) from `tabEmployee Incentive Bulk Detail` as eibd 
						join `tabEmployee Incentive Bulk` as eib on eibd.parent = eib.name
						where eib.incentive_date = '{0}'
						and eibd.employee = '{1}' and eib.salary_component = 'Production Incentive' and eib.docstatus = 1
				""".format(i['attendance_date'], i['employee']))
				i['incentive'] = employee_incentive[0][0]		
			return query
	elif 'department' not in filters and 'shift' in filters:
		query = frappe.db.sql("""
		select employee, employee_name, attendance_date, status, department, shift, working_hours 
		from `tabAttendance`
		where status = '{}'
		and attendance_date between '{}' and '{}'
		and shift = '{}'
		""".format(filters['status'], filters['from_date'], filters['to_date'], filters['shift']), as_dict=1)
		if query:
			for i in query:
				shift = 0
				shift_start = frappe.db.get_value('Shift Type',i['shift'],'start_time')
				shift_end = frappe.db.get_value('Shift Type',i['shift'],'end_time')
				if shift_end is not None and shift_start is not None:
					shift_time = shift_end - shift_start
					hours = shift_time.seconds
					total = hours//3600
					if i['working_hours'] > total:
						shift = i['working_hours'] - total
				i['ot'] = shift
				employee_incentive = frappe.db.sql("""
						select coalesce(sum(eibd.incentive_hours), 0) from `tabEmployee Incentive Bulk Detail` as eibd 
						join `tabEmployee Incentive Bulk` as eib on eibd.parent = eib.name
						where eib.incentive_date = '{0}'
						and eibd.employee = '{1}' and eib.salary_component = 'Production Incentive' and eib.docstatus = 1
				""".format(i['attendance_date'], i['employee']))
				i['incentive'] = employee_incentive[0][0]		
			return query
	else:			
		print('in else')	
		query = frappe.db.sql("""
		select employee, employee_name, attendance_date, status, department, shift, working_hours
		from `tabAttendance`
		where status = '{}'
		and attendance_date between '{}' and '{}'
		""".format(filters['status'], filters['from_date'], filters['to_date']), as_dict=1)
		if query:
			for i in query:
				shift = 0
				shift_start = frappe.db.get_value('Shift Type',i['shift'],'start_time')
				shift_end = frappe.db.get_value('Shift Type',i['shift'],'end_time')
				if shift_end is not None and shift_start is not None:
					shift_time = shift_end - shift_start
					hours = shift_time.seconds
					total = hours//3600
					if i['working_hours'] > total:
						shift = i['working_hours'] - total
				i['ot'] = shift
				employee_incentive = frappe.db.sql("""
						select coalesce(sum(eibd.incentive_hours), 0) from `tabEmployee Incentive Bulk Detail` as eibd 
						join `tabEmployee Incentive Bulk` as eib on eibd.parent = eib.name
						where eib.incentive_date = '{0}'
						and eibd.employee = '{1}' and eib.salary_component = 'Production Incentive' and eib.docstatus = 1
				""".format(i['attendance_date'], i['employee']))
				i['incentive'] = employee_incentive[0][0]			
			return query