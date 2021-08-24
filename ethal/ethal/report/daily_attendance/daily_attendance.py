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

	ud_present_count = get_present_count('UD%', filters['date'])
	ud_absent_count = get_absent_count('UD%', filters['date'])
	ud_ot = overtime('UD%', filters['date'])
	
	present_count = []
	present_count.insert(0,"Present")
	present_count.insert(1, cd_present_count[0])
	present_count.insert(2, ud_present_count[0])
	present_count.insert(3, cd_present_count[0]+ud_present_count[0])
	present_count_list = [present_count]

	absent_count = []
	absent_count.insert(0,"Absent")
	absent_count.insert(1, cd_absent_count[0])
	absent_count.insert(2, ud_absent_count[0])
	absent_count.insert(3, cd_absent_count[0]+ud_absent_count[0])
	absent_count_list = [absent_count]

	ot_count = []
	ot_count.insert(0,"OT")
	ot_count.insert(1, cd_ot[0])
	ot_count.insert(2, ud_ot[0])
	ot_count.insert(3, cd_ot[0]+ud_ot[0])
	ot_count_list = [ot_count]

	return present_count_list+absent_count_list+ot_count_list

def get_present_count(department, date):
	query = frappe.db.sql("""
	select count(a.name) from `tabAttendance` a
	join `tabDepartment` d 
	on a.department = d.name
	where a.status = 'Present'
	and d.parent_department like '{0}'
	and a.attendance_date = '{1}'
	""".format(department, date))
	return query[0]

def get_absent_count(department, date):
	query = frappe.db.sql("""
	select count(a.name) from `tabAttendance` a
	join `tabDepartment` d 
	on a.department = d.name
	where a.status in ('Absent', 'On Leave')
	and d.parent_department like '{0}'
	and a.attendance_date = '{1}'
	""".format(department, date))
	return query[0]	

def overtime(department, date):
	query = frappe.db.sql("""
	select count(a.name) from `tabAttendance` a
	join `tabDepartment` d
	on a.department = d.name
	where a.status = 'Present'
	and d.parent_department like '{0}'
	and a.attendance_date = '{1}'
	and a.working_hours > 8
	""".format(department, date), as_list=1)
	return query[0]