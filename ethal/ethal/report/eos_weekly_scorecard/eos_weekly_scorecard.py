# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime, timedelta
import ast
from frappe import _


def execute(filters=None):
	columns, data = [], []
	d = []
	# columns = ['Division:Data:150']+['Parameter:Link/EOS Weekly Report Parameter:200']+['Desired:250']+['Responsible Person:250']
	columns = [{
			"label": _("Division"),
			"fieldname": "division",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Parameter"),
			"fieldname": "parameter",
			"fieldtype": "Link",
			"options": "EOS Weekly Report Parameter",
			"width": 200
		},
		{
			"label": _("Responsible Person"),
			"fieldname": "responsible_person",
			"fieldtype": "Data",
			"width": 180
		},
		{
			"label": _("Uom"),
			"fieldname": "uom",
			"fieldtype": "Data",
			"width": 110,
		}
		]
	

	total_count_of_weeks = frappe.db.get_all('EOS Weekly Scorecard', {'to_date': ('between', [filters['from_date'], filters['to_date']]),'docstatus':1}, ['name','from_date','to_date'],order_by='from_date ASC')
	print(total_count_of_weeks)
	for i in range(1, len(total_count_of_weeks)+1):
		# d.append('Target '+'('+str(i.from_date)+" To "+ str(i.to_date)+')'+':data:100')
		target_column = {
		"label": _("Week ") + str(i),
        "fieldname": "week_" + str(i),  # Unique fieldname for each "Desired" column
        "fieldtype": "Data",
        "width": 100,
		}
		d.append(target_column)

		actual_column = {
		"label": _("Actual ") + str(i),
		"fieldname": "actual_"+ str(i), 
		"fieldtype": "Data",
		"width": 70,
		"size":20
		}
		d.append(actual_column)
		# d.append('Actual '+str(i)+':data:270')
		
		desired_column = {
        "label": _("Desired ") + str(i),
        "fieldname": "desired_",  # Unique fieldname for each "Desired" column
        "fieldtype": "Data",
        "width": 50,
        "hidden": 1  # Set hidden property to 1 to hide the column
    	}
		d.append(desired_column)
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

	# print("from date",from_date)
	# print("to date",to_date)
	# total_count_of_weeks = frappe.db.get_all('EOS Weekly Scorecard', {'to_date': ('between', [filters['from_date'], filters['to_date']])}, ['name'], order_by="name asc")
	# lst = []
	# for j in total_count_of_weeks:
	# 	a = " (select distinct A.actual from `tabEOS Weekly Scorecard Details` as A where A.parent = '{0}' and A.division=B.division and A.parameter = B.parameter and A.responsible_name = B.responsible_name and A.target = B.target and A.actual = B.actual limit 1) as actual ".format(j['name'])
	# 	lst.append(a)
	# separator = ", "
	# lst2 = separator.join(lst)
	# lst1 = []
	# for j in total_count_of_weeks:
	# 	a = " (select distinct A.target from `tabEOS Weekly Scorecard Details` as A where A.parent = '{0}' and A.division=B.division and A.parameter = B.parameter and A.responsible_name = B.responsible_name and A.actual = B.actual ) as target ".format(j['name'])
	# 	lst1.append(a)
	# separator = ", "
	# lst3 = separator.join(lst1)
	# a = [sub[item] for item in range(len(lst)) for sub in [lst1, lst]]
	# print(a)
	# lst4 = separator.join(a)
	# if lst2:
	# 	return frappe.db.sql("""
	# 			SELECT distinct B.division, B.parameter, B.responsible_name, {2}
	# 			from `tabEOS Weekly Scorecard Details` as B join `tabEOS Weekly Scorecard` 
	# 			on B.parent = `tabEOS Weekly Scorecard`.name
	# 			where `tabEOS Weekly Scorecard`.to_date between '{0}' and '{1}'
	# 			order by B.idx asc;
	# 					""".format(filters['from_date'], filters['to_date'], lst4))						

	query = ""
	selectlist = ""
	i = 1
	# for date in range(len(from_date)):
	total_count_of_weeks = frappe.db.get_all('EOS Weekly Scorecard', {'to_date': ('between', [filters['from_date'], filters['to_date']]),'docstatus':1}, ['name'], order_by="from_date asc")
	if total_count_of_weeks:
		for j in total_count_of_weeks:	
			if query == "":
				query = """ from (Select Distinct B.division, B.parameter, B.responsible_name, B.idx,B.uom from `tabEOS Weekly Scorecard` as A 
					join `tabEOS Weekly Scorecard Details` as B on A.name = B.parent 
					where A.to_date between '{0}' and '{1}' order by B.idx asc) Week{2} 
					""".format(from_date[0], to_date[-1], i)
				
				selectlist = "Select Week1.division, Week1.parameter, Week1.responsible_name,Week1.uom"
		
				# query += """ Left JOIN (select distinct B.division, B.parameter, B.responsible_name, Round(B.target,2) as target, Round(B.actual,2) as actual, B.desired  
				# 			from    `tabEOS Weekly Scorecard` as A 
				# 			join `tabEOS Weekly Scorecard Details` as B on A.name = B.parent 
				# 			where A.name = '{0}' and A.docstatus = 1) Week{1} 
				# 			ON Week1.division = Week{1}.division AND Week1.parameter = Week{1}.parameter AND Week1.responsible_name = Week{1}.responsible_name
				# 			""".format(j['name'], 'A')
				# selectlist += ",WeekA.target ,WeekA.actual,WeekA.desired".format(i)	
				query += """ 
					LEFT JOIN (
						SELECT DISTINCT
							B.division,
							B.parameter,
							B.responsible_name,
							COALESCE(Round(B.target, 2), 'NA') as target,
							COALESCE(Round(B.actual, 2), 'NA') as actual,
							COALESCE(B.desired, 'NA') as desired
						FROM
							`tabEOS Weekly Scorecard` as A 
						JOIN
							`tabEOS Weekly Scorecard Details` as B
						ON
							A.name = B.parent
						WHERE
							A.name = '{0}' and A.docstatus = 1
					) Week{1} 
					ON
						Week1.division = Week{1}.division
						AND Week1.parameter = Week{1}.parameter
						AND Week1.responsible_name = Week{1}.responsible_name
				""".format(j['name'], 'A')

				selectlist += ", COALESCE(WeekA.target, 'NA'), COALESCE(WeekA.actual, 'NA'), COALESCE(WeekA.desired, 'NA')".format(i)

										
			else:
				# query += """ Left JOIN (select distinct B.division, B.parameter, B.responsible_name, Round(B.target,2) as target, Round(B.actual,2) as actual, B.desired  
				# 			from    `tabEOS Weekly Scorecard` as A 
				# 			join `tabEOS Weekly Scorecard Details` as B on A.name = B.parent 
				# 			where  A.name = '{0}' and A.docstatus = 1 ) Week{1} 
				# 			ON Week1.division = Week{1}.division AND Week1.parameter = Week{1}.parameter AND Week1.responsible_name = Week{1}.responsible_name
				# 			""".format(j['name'], i)
				# selectlist += ",Week{0}.target ,Week{0}.actual,Week{0}.desired".format(i)	
				query += """
					LEFT JOIN (
						SELECT DISTINCT
							B.division,
							B.parameter,
							B.responsible_name,
							COALESCE(Round(B.target, 2), 'NA') as target,
							COALESCE(Round(B.actual, 2), 'NA') as actual,
							COALESCE(B.desired, 'NA') as desired
						FROM
							`tabEOS Weekly Scorecard` as A
						JOIN
							`tabEOS Weekly Scorecard Details` as B
						ON
							A.name = B.parent
						WHERE
							A.name = '{0}' and A.docstatus = 1
					) Week{1}
					ON
						Week1.division = Week{1}.division
						AND Week1.parameter = Week{1}.parameter
						AND Week1.responsible_name = Week{1}.responsible_name
				""".format(j['name'], i)

				selectlist += ", COALESCE(Week{0}.target, 'NA'), COALESCE(Week{0}.actual, 'NA'), COALESCE(Week{0}.desired, 'NA')".format(i)
						
			i+=1		
		query = selectlist+query+"order by Week1.idx"
		return frappe.db.sql(query)


	
