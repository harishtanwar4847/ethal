# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from ethal.ethal.report.liquidity_ratios.liquidity_ratios import get_monthly_gl_credit,get_monthly_gl_credit_no_opening,get_monthly_gl_debit,get_monthly_gl_debit_no_opening,get_monthly_gl_credit_20000,get_monthly_gl_debit_10000


def execute(filters=None):
	columns, data = [], []
	# columns = ["Month::180"]+["Manpower Cost - H.O.::180"]+["Financial expenses::180"]+["General & Administrative::180"]+["Non-operational::180"]
	columns = [
		{
			"label": "Month",
			"fieldname": "month",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "Manpower Cost - H.O.",
			"fieldname": "manpower_cost_ho",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "Financial expenses",
			"fieldname": "financial_expenses",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "General & Administrative",
			"fieldname": "general_and_administrative",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "Non-operational",
			"fieldname": "non_operational",
			"fieldtype": "Data",
			"width": 150
		},
	]
	data = get_data()
	return columns, data

def get_data():
	
	def manpower():
		lst_61000  = get_monthly_gl_debit_no_opening("61%")
		lst_41100 = get_monthly_gl_credit_no_opening("411%")
		final_res = [a/b if a!=0 and b!=0 else 0 for a,b in zip(lst_61000,lst_41100)]
		per_final_result = []
		for i in final_res:
			print(i)
			per_final_result.append('{:.2f}%'.format(i))
		return per_final_result

	def financial_expenses():
		lst_62000  = get_monthly_gl_debit_no_opening("62%")
		lst_41100 = get_monthly_gl_credit_no_opening("411%")
		final_res = [a/b if a!=0 and b!=0 else 0 for a,b in zip(lst_62000,lst_41100)]
		per_final_result = []
		for i in final_res:
			print(i)
			per_final_result.append('{:.2f}%'.format(i))
		return per_final_result


	def general_and_administrative():
		lst_63000  = get_monthly_gl_debit_no_opening("63%")
		lst_41100 = get_monthly_gl_credit_no_opening("411%")
		final_res = [a/b if a!=0 and b!=0 else 0 for a,b in zip(lst_63000,lst_41100)]
		per_final_result = []
		for i in final_res:
			print(i)
			per_final_result.append('{:.2f}%'.format(i))
		return per_final_result


	def non_operational():
		lst_64000  = get_monthly_gl_debit_no_opening("64%")
		lst_41100 = get_monthly_gl_credit_no_opening("411%")
		final_res = [a/b if a!=0 and b!=0 else 0 for a,b in zip(lst_64000,lst_41100)]
		per_final_result = []
		for i in final_res:
			print(i)
			per_final_result.append('{:.2f}%'.format(i))
		return per_final_result




	m = manpower()
	fe = financial_expenses()
	ga = general_and_administrative()
	nop = non_operational()
	month = ["Jan","Feb","Mar","April","May","June","July","Aug","Sept","Oct","Nov","Dec"]
	res = []
	for (i,j,k,l,m) in zip(month,m,fe,ga,nop):
		res.append([i,j,k,l,m])
	return res