# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	columns = ['Attendance:Data:120']
	working_area_list = frappe.db.get_all('Working Area', ['name'])
	
	for i in working_area_list:
		columns += [i['name']+ ':Link/Working Area']
	columns = columns + ['Total:150']	
	
	attendance = ['Present', 'Absent', 'OT', 'Incentive']
	present = [attendance[0]]
	absent = [attendance[1]]
	ot = [attendance[2]]
	incentives = [attendance[3]]
	present_count = 0
	absent_count = 0
	ot_count = 0
	incentives_count = 0
	for k in attendance:
		for j in working_area_list:
			if k in ('Present', 'Absent'):
				query = frappe.db.sql("""
				select count(a.name) from `tabAttendance` a
				join `tabEmployee` emp 
				on a.employee = emp.name
				where a.status = '{0}'
				and a.attendance_date = '{1}'
				and a.working_area = '{2}'
				and a.docstatus = 1
				""".format(k, filters['date'], j['name']))
				if query and k == 'Present': 
					present_count += query[0][0]
					present.append(query[0][0])
				elif query and k in ('Absent', 'On Leave'):
					absent.append(query[0][0])	
					absent_count += query[0][0]
			elif k == 'OT':
				query = frappe.db.sql("""
				select a.working_hours from `tabAttendance` a
				join `tabEmployee` emp
				on a.employee = emp.name
				where a.status = '{0}'
				and a.attendance_date = '{1}'
				and a.working_area = '{2}'
				and a.working_hours > 8
				and a.docstatus = 1
				""".format(k, filters['date'], j['name']), as_list=1)
				addition_value = []
				for i in query:
					addition_value.append(i[0]-8)
				if len(addition_value) != 0:	
					ot.append(sum(addition_value))
					ot_count += sum(addition_value)
				else:
					ot.append(0)
					ot_count += 0
			elif k == 'Incentive':
				query = frappe.db.sql("""
				select name from `tabEmployee Incentive Bulk` 
				where incentive_date = '{}' and salary_component = 'Production Incentive'
				and docstatus = 1
				""".format(filters['date']))
		
				if query:	
					a = []
					for i in query:
						get_details = frappe.db.sql("""
						select coalesce(sum(eibd.incentive_hours), 0) 
						from `tabEmployee Incentive Bulk Detail` eibd
						join `tabEmployee` emp
						on eibd.employee = emp.name
						and emp.working_area = '{1}'
						where eibd.parent = '{0}' 
						""".format(i[0], j['name']))
						
						a.append(get_details[0][0])
					incentives.append(sum(a))
					incentives_count += sum(a)
				else:
					incentives.append(0)				
	present.append(present_count)
	absent.append(absent_count)
	ot.append(ot_count)
	incentives.append(incentives_count)		
	data = [present, absent, ot, incentives]
	
	return columns, data