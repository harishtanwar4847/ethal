# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	columns = ['Annealing:Link/Annealing:200']+['In Time:Datetime:100']+['Out Time:Datetime:100']+['KG:Float']
	data = get_data(filters)
	return columns, data

def get_data(filters):
	if filters.annealing:
		return frappe.db.sql(""" 
			select parent, in_time, out_time, kg
			from `tabAnnealing Items`
			where parent = '{}'
			order by parent
		""".format(filters.annealing))
	else:
		return frappe.db.sql(""" 
		select parent, in_time, out_time, kg
		from `tabAnnealing Items`
		order by parent
	""")