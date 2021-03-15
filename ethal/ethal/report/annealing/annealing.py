# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	columns = ['Annealing:Link/Annealing:200']+['In Time:Datetime:180']+['Out Time:Datetime:180']+['KG:Float:200']
	data = get_data(filters)
	return columns, data

def get_data(filters):
	print(filters.from_date)
	if filters.annealing:
		return frappe.db.sql(""" 
			select parent, in_time, out_time, kg
			from `tabAnnealing Items`
			where parent = '{0}'
			order by parent
		""".format(filters.annealing))
	elif filters.from_date and filters.to_date:
		return frappe.db.sql(""" 
			select ai.parent, ai.in_time, ai.out_time, ai.kg
			from `tabAnnealing Items` as ai
			join `tabAnnealing` as a
			on a.name = ai.parent
			where a.date between '{0}' and '{1}'
			order by a.name
		""".format(filters.from_date, filters.to_date))	
	elif filters.annealing and filters.from_date and filters.to_date:
		return frappe.db.sql(""" 
			select ai.parent, ai.in_time, ai.out_time, ai.kg
			from `tabAnnealing Items` as ai
			join `tabAnnealing` as a
			on a.name = ai.parent
			where ai.parent = '{0}'
			and a.date between {1} and {2}
			order by a.name
		""".format(filters.annealing, filters.from_date, filters.to_date))
	else:
		return frappe.db.sql(""" 
		select parent, in_time, out_time, kg
		from `tabAnnealing Items`
		order by parent
	""")