# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	columns = ['Sales Invoice:Link/Sales Invoice:250']+['Items:Link/Item:250']+['Net Weight:Float:150']+['Amount:Currency:150']+['Cost Per KG:Float:150']
	data = get_data(filters)
	return columns, data

def get_data(filters):
	if filters:
		return frappe.db.sql("""
				select parent, item_code, total_net_weight, amount, (amount/total_net_weight) 
				from `tabSales Invoice Item`
				where docstatus != 2 and creation between '{0}' and '{1}'
				group by parent, item_code desc;
			""".format(filters['from_date'], filters['to_date']))