# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	columns = [
		{
			"label": "Month",
			"fieldname": "month",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "Sales",
			"fieldname": "sales",
			"fieldtype": "Currency",
			"width": 200
		}
	]
	data = get_data()
	return columns, data

def sales_invoice():
	return frappe.db.sql(""" select sum(total) from `tabSales Invoice`
	 where YEAR(posting_date) = 2020 GROUP BY MONTH(posting_date) 
	 ORDER BY posting_date;
	 """, as_list=True)

def sales_invoice_qty():
	return frappe.db.sql(""" select sum(total_net_weight_aluminium/100) from `tabSales Invoice`
	 where YEAR(posting_date) = 2020 GROUP BY MONTH(posting_date) 
	 ORDER BY posting_date;
	 """, as_list=True)

def get_data():
	month = ["Jan","Feb","Mar","April","May","June","July","Aug","Sept","Oct","Nov","Dec"]
	sales_invoice_list = sales_invoice()
	print(sales_invoice_list)
	sales_invoice_qty_list = sales_invoice_qty()
	print(sales_invoice_qty_list)
	# divide = [b/100 if b!=0 else 0 for b in zip(sales_invoice_qty_list)]
	# print(divide)
	calculate = [a[0]/b[0] if a[0]!=0 and b[0]!=0 else 0 for a,b in zip(sales_invoice_list,sales_invoice_qty_list)]
	print(calculate)
	res = []
	for (i,j) in zip(month,calculate):
		res.append([i,j])
	return res



