# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from ethal.ethal.report.liquidity_ratios.liquidity_ratios import get_monthly_gl_credit,get_monthly_gl_credit_no_opening,get_monthly_gl_debit,get_monthly_gl_debit_no_opening,get_monthly_gl_credit_20000,get_monthly_gl_debit_10000

def execute(filters=None):
	columns, data = [], []
	# columns = ["Month::180"]+["DB sales % ::180"]+["TU sales % ::180"]
	columns = [
		{
			"label": "Month",
			"fieldname": "month",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "DB sales %",
			"fieldname": "db_sales_per",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "TU sales %",
			"fieldname": "tu_sales_per",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "DB sales Amount",
			"fieldname": "db_sales",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": "TU sales Amount",
			"fieldname": "tu_sales",
			"fieldtype": "Currency",
			"width": 150
		}
	]
	data = get_data()
	return columns, data

def get_data():
	
	def db_sales_percent():
		lst_41110 = get_monthly_gl_credit_no_opening("4111%")
		lst_41100 = get_monthly_gl_credit_no_opening("411%")
		final_res = [a / f*100 if a!=0 and f!=0 else 0 for a,f in zip(lst_41110, lst_41100)]
		per_final_result = []
		for i in final_res:
			print(i)
			per_final_result.append('{:.2f}%'.format(i))
		return per_final_result

	def tu_sales_percent():
		lst_41120 = get_monthly_gl_credit_no_opening("4112%")
		lst_41100 = get_monthly_gl_credit_no_opening("411%")
		final_res = [a / f*100 if a!=0 and f!=0 else 0 for a,f in zip(lst_41120, lst_41100)]
		per_final_result = []
		for i in final_res:
			print(i)
			per_final_result.append('{:.2f}%'.format(i))
		return per_final_result

	def db_sales():
		lst_41110 = get_monthly_gl_credit_no_opening("4111%")
		lst_41100 = get_monthly_gl_credit_no_opening("411%")
		final_res = [a / f if a!=0 and f!=0 else 0 for a,f in zip(lst_41110, lst_41100)]
		return final_res

	def tu_sales():
		lst_41120 = get_monthly_gl_credit_no_opening("4112%")
		lst_41100 = get_monthly_gl_credit_no_opening("411%")
		final_res = [a / f if a!=0 and f!=0 else 0 for a,f in zip(lst_41120, lst_41100)]
		return final_res

	dsp = db_sales_percent()
	tsp = tu_sales_percent()
	dp = db_sales()
	tu = tu_sales()
	month = ["Jan","Feb","Mar","April","May","June","July","Aug","Sept","Oct","Nov","Dec"]
	res = []
	for (i,j,k,l,m) in zip(month,dsp,tsp,dp,tu):
		res.append([i,j,k,l,m])
	return res