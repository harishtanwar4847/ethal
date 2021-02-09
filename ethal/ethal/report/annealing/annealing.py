# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	columns = ['In Time:Date:100']+['Out Time:Date:100']+['KG:Float:100']
	data = get_data(filters)
	return columns, data

def get_data(filters):
	return frappe.db.sql("""
		select 
			in_time, out_time, kg 
		from 
			`tabAnnealing Items`
		where
			parent = '{}'
	""".format(filters.annealing))	
