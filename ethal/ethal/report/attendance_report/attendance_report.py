# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns, data = [], []
	columns = ['Employee:Link/Employee:200']+['Employee Name:Data:250']+['Attendance Date:Date:150']+['Status:Data:200']+['Department:Link/Department:200']+['Shift:Link/Shift Type:150']+['Working Hours:Float:150']+['OT:Float:150']+['Incentive:Float:150']
	data = get_data(filters)
	return columns, data

def get_data(filters):
	if 'department' in filters and 'working_area' in filters and 'shift' not in filters and 'status' not in filters:
		print('in department and working area')
		condition = "where att.docstatus = 1 and att.attendance_date between '{}' and '{}' and att.department = '{}' and emp.working_area = '{}'".format(filters['from_date'], filters['to_date'], filters['department'], filters['working_area'])
		return query_condition(condition)	
	elif 'department' not in filters and 'working_area' in filters and 'shift' not in filters and 'status' not in filters:
		condition = "where att.docstatus = 1 and att.attendance_date between '{}' and '{}' and emp.working_area = '{}'".format(filters['from_date'], filters['to_date'], filters['working_area'])
		print('in working area')
		return query_condition(condition)
	elif 'department' not in filters and 'working_area' not in filters and 'shift' in filters and 'status' not in filters:
		print('in shift')
		condition = "where att.docstatus = 1 and att.attendance_date between '{}' and '{}' and att.shift = '{}'".format(filters['from_date'], filters['to_date'], filters['shift'])
		return query_condition(condition)
	elif 'department' in filters and 'working_area' not in filters and 'shift' not in filters and 'status' not in filters:
		print('in department')
		condition = "where att.docstatus = 1 and att.attendance_date between '{}' and '{}' and att.department = '{}'".format(filters['from_date'], filters['to_date'], filters['department'])
		return query_condition(condition)	
	elif 'department' not in filters and 'working_area' not in filters and 'shift' not in filters and 'status' in filters:
		print('in status')
		condition = "where att.docstatus = 1 and att.status = '{}' and att.attendance_date between '{}' and '{}'".format(filters['status'], filters['from_date'], filters['to_date'])
		return query_condition(condition)							
	elif 'department' in filters and 'shift' in filters and 'working_area' in filters and 'status' not in filters:
		print('department and shift and working area')
		condition = "where att.docstatus = 1 and att.attendance_date between '{}' and '{}' and att.department = '{}' and att.shift = '{}' and emp.working_area = '{}'".format(filters['from_date'], filters['to_date'], filters['department'], filters['shift'], filters['working_area'])
		return query_condition(condition)
	elif 'department' in filters and 'shift' in filters and 'working_area' not in filters and 'status' in filters:
		print('department and shift and status')
		condition = "where att.docstatus = 1 and att.status = '{}' and att.attendance_date between '{}' and '{}' and att.department = '{}' and att.shift = '{}'".format(filters['status'], filters['from_date'], filters['to_date'], filters['department'], filters['shift'])
		return query_condition(condition)
	elif 'department' in filters and 'shift' not in filters and 'working_area' in filters and 'status' in filters:
		print('department and status and working area')
		condition = "where att.docstatus = 1 and att.status = '{}' and att.attendance_date between '{}' and '{}' and att.department = '{}' and emp.working_area = '{}'".format(filters['status'], filters['from_date'], filters['to_date'], filters['department'], filters['working_area'])
		return query_condition(condition)
	elif 'department' not in filters and 'shift' in filters and 'working_area' in filters and 'status' in filters:
		print('shift and status and working area')
		condition = "where att.docstatus = 1 and att.status = '{}' and att.attendance_date between '{}' and '{}' and emp.working_area = '{}' and att.shift = '{}'".format(filters['status'], filters['from_date'], filters['to_date'], filters['working_area'], filters['shift'])
		return query_condition(condition)
	elif 'department' in filters and 'shift' in filters and 'working_area' in filters and 'status' in filters:
		print('shift and status and working area and department')
		condition = "where att.docstatus = 1 and att.status = '{}' and att.attendance_date between '{}' and '{}' and att.department = '{}' and emp.working_area = '{}' and att.shift = '{}'".format(filters['status'], filters['from_date'], filters['to_date'], filters['department'], filters['working_area'], filters['shift'])
		return query_condition(condition)
	elif 'department' in filters and 'shift' not in filters and 'working_area' in filters and 'status' not in filters:
		print('department and working area')
		condition = "where att.docstatus = 1 and att.attendance_date between '{}' and '{}' and att.department = '{}' and emp.working_area = '{}'".format(filters['from_date'], filters['to_date'], filters['department'], filters['working_area'])
		return query_condition(condition)
	elif 'department' not in filters and 'shift' in filters and 'working_area' in filters and 'status' not in filters:
		print('shift and working area')
		condition = "where att.docstatus = 1 and att.attendance_date between '{}' and '{}' and att.shift = '{}' and emp.working_area = '{}'".format(filters['from_date'], filters['to_date'], filters['shift'], filters['working_area'])
		return query_condition(condition)
	elif 'department' in filters and 'shift' in filters and 'working_area' not in filters and 'status' not in filters:
		print('shift and department area')
		condition = "where att.docstatus = 1 and att.attendance_date between '{}' and '{}' and att.shift = '{}' and att.department = '{}'".format(filters['from_date'], filters['to_date'], filters['shift'], filters['department'])
		return query_condition(condition)
	elif 'department' not in filters and 'shift' in filters and 'working_area' not in filters and 'status' in filters:
		print('shift and status ')
		condition = "where att.docstatus = 1 and att.status = '{}' and att.attendance_date between '{}' and '{}' and att.shift = '{}'".format(filters['status'], filters['from_date'], filters['to_date'], filters['shift'])
		return query_condition(condition)	
	elif 'department' in filters and 'shift' not in filters and 'working_area' not in filters and 'status' in filters:
		print('department and status ')
		condition = "where att.docstatus = 1 and att.status = '{}' and att.attendance_date between '{}' and '{}' and att.department = '{}'".format(filters['status'], filters['from_date'], filters['to_date'], filters['department'])
		return query_condition(condition)
	elif 'department' not in filters and 'shift' not in filters and 'working_area' in filters and 'status' in filters:
		print('working area and status ')
		condition = "where att.docstatus = 1 and att.status = '{}' and att.attendance_date between '{}' and '{}' and emp.working_area = '{}'".format(filters['status'], filters['from_date'], filters['to_date'], filters['working_area'])
		return query_condition(condition)	
	else:			
		print('in else')	
		condition = "where att.docstatus = 1 and att.status = '{}' and attendance_date between '{}' and '{}'".format(filters['status'], filters['from_date'], filters['to_date'])
		return query_condition(condition)

def query_condition(condition):
	query = frappe.db.sql("""
		select att.employee, att.employee_name, att.attendance_date, att.status, att.department, att.shift, att.working_hours 
		from `tabAttendance` att
		join `tabEmployee` emp
		on att.employee = emp.name
		{}
		""".format(condition), as_dict=1)
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