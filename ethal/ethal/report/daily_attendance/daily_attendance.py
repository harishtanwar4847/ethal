# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	columns = ['Attendance:Data:200']+['Circle Section:Int:100']+['Utensil Section:Int:100']+['Total:Int:100']
	data = get_data(filters)

	return columns, data

def get_data(filters):
	cd_present_count = get_present_count('CD%', filters['date'])
	cd_absent_count = get_absent_count('CD%', filters['date'])
	cd_ot = overtime('CD%', filters['date'])
	cd_incentive = incentives('CD%', filters['date'])
	
	ud_present_count = get_present_count('UD%', filters['date'])
	ud_absent_count = get_absent_count('UD%', filters['date'])
	ud_ot = overtime('UD%', filters['date'])
	ud_incentive = incentives('UD%', filters['date'])
	
	present_count = []
	present_count.insert(0,"Present")
	present_count.insert(1, cd_present_count)
	present_count.insert(2, ud_present_count)
	present_count.insert(3, cd_present_count+ud_present_count)
	present_count_list = [present_count]

	absent_count = []
	absent_count.insert(0,"Absent")
	absent_count.insert(1, cd_absent_count)
	absent_count.insert(2, ud_absent_count)
	absent_count.insert(3, cd_absent_count+ud_absent_count)
	absent_count_list = [absent_count]

	ot_count = []
	ot_count.insert(0,"OT")
	ot_count.insert(1, cd_ot)
	ot_count.insert(2, ud_ot)
	ot_count.insert(3, cd_ot+ud_ot)
	ot_count_list = [ot_count]

	incentive = []
	incentive.insert(0,"Incentive")
	incentive.insert(1, cd_incentive)
	incentive.insert(2, ud_incentive)
	incentive.insert(3, cd_incentive+ud_incentive)
	incentive_list = [incentive]

	return present_count_list+absent_count_list+ot_count_list+incentive_list

def get_present_count(department, date):
	query = frappe.db.sql("""
	select count(a.name) from `tabAttendance` a
	join `tabDepartment` d 
	on a.department = d.name
	where a.status = 'Present'
	and d.parent_department like '{0}'
	and a.attendance_date = '{1}'
	""".format(department, date))
	if query:
		return query[0][0]

def get_absent_count(department, date):
	query = frappe.db.sql("""
	select count(a.name) from `tabAttendance` a
	join `tabDepartment` d 
	on a.department = d.name
	where a.status in ('Absent', 'On Leave')
	and d.parent_department like '{0}'
	and a.attendance_date = '{1}'
	""".format(department, date))
	if query:
		return query[0][0]	

def overtime(department, date):
	query = frappe.db.sql("""
	select a.working_hours from `tabAttendance` a
	join `tabDepartment` d
	on a.department = d.name
	where a.status = 'Present'
	and d.parent_department like '{0}'
	and a.attendance_date = '{1}'
	and a.working_hours > 8
	""".format(department, date), as_list=1)
	addition_value = []
	for i in query:
		addition_value.append(i[0]-8)
	if len(addition_value) != 0:	
		return sum(addition_value)
	else:
		return 0

def incentives(department, date):
	query = frappe.db.sql("""
	select name from `tabEmployee Incentive Bulk` 
	where incentive_date = '{}' and salary_component = 'Production Incentive'
	""".format(date))	
	if query:	
		a = []
		for i in query:
			get_details = frappe.db.sql("""
			select coalesce(sum(eibd.incentive_hours), 0) 
			from `tabEmployee Incentive Bulk Detail` eibd
			join `tabDepartment` d
			on eibd.department = d.name
			where eibd.parent = '{0}' and eibd.department like '{1}'
			""".format(i[0], department))
			print(get_details)
			a.append(get_details[0][0])
		return sum(a)
	else:
		return 0		
