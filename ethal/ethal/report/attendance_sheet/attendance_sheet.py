# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	columns = ['Full Name:Data:300']+['Department:Link/Department:200']+['Shift:Data:150']+['In Time:Data:150']+['Out Time:Data:150']+['Working Hours:Data:100']+['OT:Data:100']+['Fixed Incentive:Data:100']+['Production:Data:100']
	data = get_data(filters)
	return columns, data

def get_data(filters):
	return frappe.db.sql("""
	select employee_name, department from `tabEmployee` 
	where status = 'Active'
	and department = '{}'
	""".format(filters['department']))