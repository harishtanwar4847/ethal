# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime, timedelta
import ast

def execute(filters=None):
	columns, data = [], []
	
	date1 = filters['from_date']
	a = datetime.strptime(date1, '%Y-%m-%d')
	date2 = filters['to_date']
	b = datetime.strptime(date2, '%Y-%m-%d')
	days = abs(a-b).days
	c = (days//7)
	d = []
	for i in range(1, c+1):
		d.append('Week '+str(i)+':data:100')
	columns = ['Parameter:Data:200']+['Responsible Person:Link/Employee:250']+['Target:Float:150']
	data = get_data(filters)
	return columns+d, data

def get_data(filters):
	
	sdate = datetime.strptime(filters['from_date'], '%Y-%m-%d')   # start date
	edate = datetime.strptime(filters['to_date'], '%Y-%m-%d')   # end date

	delta = edate - sdate       # as timedelta
	lst = []
	for i in range(delta.days + 1):
		day = sdate + timedelta(days=i)
		lst.append(day)
			
	from_date = []
	to_date = []
	temp_date = None
	for j in lst:
		today = j
		start = today - timedelta(days=today.weekday())
		end = start + timedelta(days=6)
		if temp_date != start or from_date.count == 0:
			from_date.append(start.strftime('%Y-%m-%d'))
			to_date.append(end.strftime('%Y-%m-%d'))
			temp_date = start

	from_date[0] = filters['from_date']
	to_date[-1] = filters['to_date']
	
	query = ""
	subquery = ""
	subquerylist= []
	for date in range(len(from_date)):
		subquery = ""
		for date1 in range(len(from_date)):	
			if date1 != 0:
				subquery += ','
			if date1 == date:
				subquery += " actual " 
			else:
				subquery += " null " 
		subquerylist.append(subquery)

	for date in range(len(from_date)):
		if query == "":
			query = """ SELECT parameter,responsibility,target, {2}
					from `tabEOS Weekly Scorecard Details`
					join `tabEOS Weekly Scorecard` 
					on `tabEOS Weekly Scorecard Details`.parent = `tabEOS Weekly Scorecard`.name
					where `tabEOS Weekly Scorecard`.to_date between '{0}' and '{1}'
					""".format(from_date[date], to_date[date], subquerylist[date])
					
		else:
			query += """ Union All SELECT parameter,responsibility,target, {2}
					from `tabEOS Weekly Scorecard Details`
					join `tabEOS Weekly Scorecard` 
					on `tabEOS Weekly Scorecard Details`.parent = `tabEOS Weekly Scorecard`.name
					where `tabEOS Weekly Scorecard`.to_date between '{0}' and '{1}'
					""".format(from_date[date], to_date[date], subquerylist[date])
	
	if filters:
		return frappe.db.sql(query)