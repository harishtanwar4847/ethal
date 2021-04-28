# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime, timedelta
import ast

def execute(filters=None):
	columns, data = [], []
	d = []
	columns = ['Division:Data:150']+['Parameter:Link/EOS Weekly Report Parameter:200']+['Responsible Person:250']+['Target:Float:150']
	total_count_of_weeks = frappe.db.get_all('EOS Weekly Scorecard', {'to_date': ('between', [filters['from_date'], filters['to_date']])}, ['name'])
	for i in range(1, len(total_count_of_weeks)+1):
		d.append('Week '+str(i)+':data:100')

	data = get_data(filters)
	return columns+d, data

def get_data(filters):
	
	total_count_of_weeks = frappe.db.get_all('EOS Weekly Scorecard', {'to_date': ('between', [filters['from_date'], filters['to_date']])}, ['name'], order_by="name asc")
	print(total_count_of_weeks)
	lst = []
	for j in total_count_of_weeks:
		a = " (select actual from `tabEOS Weekly Scorecard Details` as A where A.parent = '{0}' and A.division=B.division and A.parameter = B.parameter and A.responsible_name = B.responsible_name) as actual ".format(j['name'])
		lst.append(a)
	separator = ", "
	lst2 = separator.join(lst)
	if lst2:
		query = frappe.db.sql("""
				SELECT distinct B.division, B.parameter, B.responsible_name, B.target, {2}
				from `tabEOS Weekly Scorecard Details` as B join `tabEOS Weekly Scorecard` 
				on B.parent = `tabEOS Weekly Scorecard`.name
				where `tabEOS Weekly Scorecard`.to_date between '{0}' and '{1}'
				order by B.idx asc;
						""".format(filters['from_date'], filters['to_date'], lst2))		
	if filters:
		return query