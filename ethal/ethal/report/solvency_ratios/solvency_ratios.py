# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from ethal.ethal.report.liquidity_ratios.liquidity_ratios import get_monthly_gl_credit,get_monthly_gl_debit,get_monthly_gl_credit_20000,get_monthly_gl_debit_10000, get_monthly_gl_credit_no_opening, get_monthly_gl_debit_no_opening

def execute(filters=None):
	columns, data = [], []
	data = get_data()
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

def get_data():
	def debts_to_assets():
		lst_10000 = get_monthly_gl_debit_10000("1")
		lst_20000 = get_monthly_gl_credit_20000("2")

		final = [(b / m)*100 if m != 0 and b!=0 else 0 for b,m in zip(lst_20000,lst_10000)]
		per_final_result = []
		for i in final:
			per_final_result.append('{:.2f}%'.format(i))
		return per_final_result
	
	def debts_to_equity():
		lst_20000 = get_monthly_gl_credit_20000("2")
		lst_30000 = get_monthly_gl_debit("3")
		lst_40000 = get_monthly_gl_debit("4")
		lst_50000 = get_monthly_gl_debit("5")
		lst_60000 = get_monthly_gl_debit("6")

		deno = [(a+(b-c-d)) for a,b,c,d in zip(lst_30000,lst_40000,lst_50000,lst_60000)]
		final = [(a/b)*100 if a!= 0 and b!=0 else 0 for a,b in zip(lst_20000,deno)]
		per_final_result = []
		for i in final:
			per_final_result.append('{:.2f}%'.format(i))
		return per_final_result

	def interest_coverage():
		lst_40000 = get_monthly_gl_credit_no_opening("4")
		print(lst_40000)
		lst_50000 = get_monthly_gl_debit_no_opening("5")
		lst_60000 = get_monthly_gl_debit_no_opening("6")
		lst_62000 = get_monthly_gl_debit_no_opening("62")

		deno = [(a-b-c+d) for a,b,c,d in zip(lst_40000,lst_50000,lst_60000,lst_62000)]
		final = [(a/b) if a!= 0 and b!=0 else 0 for a,b in zip(deno, lst_62000)]
		return final
		# per_final_result = []
		# for i in final:
		# 	print(i)
		# 	per_final_result.append('{:.2f}%'.format(i))
		# return per_final_result

	# total_liability_10000 = total_liability_10000()
	# total_equity = total_equity()
	dta = debts_to_assets()	
	debts_to_equity = debts_to_equity() 
	interst = interest_coverage()
	month = ["Jan","Feb","Mar","April","May","June","July","Aug","Sept","Oct","Nov","Dec"]
	res = []
	for (i,j,k,l) in zip(month,dta,debts_to_equity,interst):
		res.append([i,j,k,l])
	
	return res