# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	columns = ['ID:Link/EOS Weekly Scorecard:200']+['Division:Data:100']+['Responsible Person:Link/Employee:250']+['Parameter:Data:200']+['UOM:Data:100']+['Target:Float:150']+['Actual:Float:150']+['Remarks:Text:250']
	data = get_data(filters)
	return columns, data

def get_data(filters):
	if filters:
		return frappe.db.sql("""
			select parent, division, responsibility, parameter, uom, target, actual, remarks
			from `tabEOS Weekly Scorecard Details`
			where creation between '{0}' and '{1}'
			""".format(filters['from_date'], filters['to_date']))