# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from ethal.ethal.report.liquidity_ratios.liquidity_ratios import get_monthly_gl_credit,get_monthly_gl_debit,get_monthly_gl_credit_20000,get_monthly_gl_debit_10000, get_monthly_gl_credit_no_opening, get_monthly_gl_debit_no_opening

def execute(filters=None):
	columns, data = [], []
	data = get_data(filters)
	# columns = ["Month::180"]+["Debts to Assets::180"]+["Debts to Equity::180"]
	columns = [
		{
			"label": "Month",
			"fieldname": "month",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "Debts to Assets",
			"fieldname": "debts_to_assets",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "Debts to Equity",
			"fieldname": "debts_to_enquiry",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "Interest Coverage",
			"fieldname": "interest_coverage",
			"fieldtype": "Data",
			"width": 150
		}
	]
	return columns, data

def get_data(filters):
	def debts_to_assets(filters):
		lst_10000 = get_monthly_gl_debit_10000("1", filters)
		lst_20000 = get_monthly_gl_credit_20000("2", filters)

		final = [(b / m)*100 if m != 0 and b!=0 else 0 for b,m in zip(lst_20000,lst_10000)]
		per_final_result = []
		for i in final:
			per_final_result.append('{:.2f}%'.format(i))
		return per_final_result
	
	def debts_to_equity(filters):
		lst_20000 = get_monthly_gl_credit_20000("2", filters)
		lst_30000 = get_monthly_gl_debit("3", filters)
		lst_40000 = get_monthly_gl_debit("4", filters)
		lst_50000 = get_monthly_gl_debit("5", filters)
		lst_60000 = get_monthly_gl_debit("6", filters)

		deno = [(a+(b-c-d)) for a,b,c,d in zip(lst_30000,lst_40000,lst_50000,lst_60000)]
		final = [(a/b)*100 if a!= 0 and b!=0 else 0 for a,b in zip(lst_20000,deno)]
		per_final_result = []
		for i in final:
			per_final_result.append('{:.2f}%'.format(i))
		return per_final_result

	def interest_coverage(filters):
		lst_40000 = get_monthly_gl_credit_no_opening("4", filters)
		print(lst_40000)
		lst_50000 = get_monthly_gl_debit_no_opening("5", filters)
		lst_60000 = get_monthly_gl_debit_no_opening("6", filters)
		lst_62000 = get_monthly_gl_debit_no_opening("62", filters)

		deno = [(a-b-c+d) for a,b,c,d in zip(lst_40000,lst_50000,lst_60000,lst_62000)]
		final = [(a/b) if a!= 0 and b!=0 else 0 for a,b in zip(deno, lst_62000)]
		per_final_result = []
		for i in final:
			print(i)
			per_final_result.append('{:.2f}%'.format(i))
		return per_final_result

	# total_liability_10000 = total_liability_10000()
	# total_equity = total_equity()
	dta = debts_to_assets(filters)	
	debts_to_equity = debts_to_equity(filters) 
	interst = interest_coverage(filters)
	month = ["Jan","Feb","Mar","April","May","June","July","Aug","Sept","Oct","Nov","Dec"]
	res = []
	for (i,j,k,l) in zip(month,dta,debts_to_equity,interst):
		res.append([i,j,k,l])
	
	return res