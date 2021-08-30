# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from ethal.ethal.report.rate___mt_sales.rate___mt_sales import sales_invoice_qty
from ethal.ethal.report.ofcf_cash_flow_report.ofcf_cash_flow_report import get_monthly_gl_debit_no_opening

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
			"label": "Manpower cost - HO/Total MT Sold",
			"fieldname": "manpower_cost",
			"fieldtype": "Currency",
			"width": 200
		},
		{
			"label": "Financial expenses - HO/Total MT Sold",
			"fieldname": "financial_expenses",
			"fieldtype": "Currency",
			"width": 200
		},
		{
			"label": "General & Admin costs / Total MT Sold",
			"fieldname": "general_admin_costs",
			"fieldtype": "Currency",
			"width": 200
		},
		{
			"label": "Non-operational expense/Total MT Sold",
			"fieldname": "non_operational_expenses",
			"fieldtype": "Currency",
			"width": 150
		}
	]
	data = get_data(filters)
	return columns, data

def get_data(filters):

	def manpower_cost(filters):
		lst_61000 = get_monthly_gl_debit_no_opening("61000%", filters)
		sales_invoice = sales_invoice_qty()
		final_res = [(a/e[0]) if e[0]!=0 else 0 for a,e in zip(lst_61000, sales_invoice)]
		return final_res

	def financial_expenses(filters):
		lst_62000 = get_monthly_gl_debit_no_opening("62000%", filters)
		sales_invoice = sales_invoice_qty()
		final_res = [(a/b[0]) if b[0]!=0 else 0 for a,b in zip(lst_62000, sales_invoice)]
		return final_res

	def general_admin_costs(filters):
		lst_63000 = get_monthly_gl_debit_no_opening("63000%", filters)
		sales_invoice = sales_invoice_qty()
		final_res = [(a/b[0]) if b[0]!=0 else 0 for a,b in zip(lst_63000, sales_invoice)]
		return final_res

	def non_operational_expenses(filters):
		lst_64000 = get_monthly_gl_debit_no_opening("64000%", filters)
		sales_invoice = sales_invoice_qty()
		final_res = [(a/b[0]) if b[0]!=0 else 0 for a,b in zip(lst_64000, sales_invoice)]
		return final_res

	manpower = manpower_cost(filters)
	financial = financial_expenses(filters)
	general = general_admin_costs(filters)
	operational = non_operational_expenses(filters)
	month = ["Jan","Feb","Mar","April","May","June","July","Aug","Sept","Oct","Nov","Dec"]
	res = []
	for (i,j,k,l,m) in zip(month,manpower,financial,general,operational):
		res.append([i,j,k,l,m])
	return res