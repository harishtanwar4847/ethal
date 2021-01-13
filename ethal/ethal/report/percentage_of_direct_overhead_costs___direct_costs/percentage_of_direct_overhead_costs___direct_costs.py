# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from ethal.ethal.report.liquidity_ratios.liquidity_ratios import get_monthly_gl_credit,get_monthly_gl_credit_no_opening,get_monthly_gl_debit,get_monthly_gl_debit_no_opening,get_monthly_gl_credit_20000,get_monthly_gl_debit_10000


def execute(filters=None):
	columns, data = [], []
	# columns = ["Month::180"]+["Direct Material as a % of total costs ::180"]+["Fuel ::180"]+["Manpower Cost - Factory ::180"]+["Stores & Repairs ::180"]+["Utilities - Electricity & Water ::180"]
	columns = [
		{
			"label": "Month",
			"fieldname": "month",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "Direct Material as a % of total costs",
			"fieldname": "direct_material",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "Fuel",
			"fieldname": "fuel",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "Manpower Cost - Factory",
			"fieldname": "manpower_cost",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "Stores & Repairs",
			"fieldname": "stores_repair",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "Utilities - Electricity & Water",
			"fieldname": "utilities_electricity",
			"fieldtype": "Data",
			"width": 150
		}
	]
	
	data = get_data(filters)
	return columns, data

def get_data(filters):
	
	def direct_material(filters):
		lst_51000_01 = get_monthly_gl_debit_no_opening("51000-01", filters)
		lst_51000_02 = get_monthly_gl_debit_no_opening("51000-02", filters)
		lst_52000_01 = get_monthly_gl_debit_no_opening("52000-01", filters)
		lst_53000_01 = get_monthly_gl_debit_no_opening("53000-01", filters)
		lst_50000 = get_monthly_gl_credit_no_opening("5%", filters)
		numeratr = [a+b+c+d for a,b,c,d in zip(lst_51000_01,lst_51000_02,lst_52000_01,lst_53000_01)]
		final_res = [a/b if a!=0 and b!=0 else 0 for a,b in zip(numeratr,lst_50000)]
		per_final_result = []
		for i in final_res:
			print(i)
			per_final_result.append('{:.2f}%'.format(i))
		return per_final_result


	def fuel(filters):
		lst_51000_03 = get_monthly_gl_debit_no_opening("51000-03", filters)
		lst_50000 = get_monthly_gl_credit_no_opening("5%", filters)
		final_res = [a/b if a!=0 and b!=0 else 0 for a,b in zip(lst_51000_03,lst_50000)]
		per_final_result = []
		for i in final_res:
			print(i)
			per_final_result.append('{:.2f}%'.format(i))
		return per_final_result


	def manpower_cost(filters):
		lst_51000_04 = get_monthly_gl_debit_no_opening("51000-04", filters)
		lst_51000_02 = get_monthly_gl_debit_no_opening("52000-02", filters)
		lst_53000_02 = get_monthly_gl_debit_no_opening("53000-02", filters)
		lst_54100 = get_monthly_gl_debit_no_opening("541%", filters)
		lst_50000 = get_monthly_gl_credit_no_opening("5%", filters)
		numeratr = [a+b+c+d for a,b,c,d in zip(lst_51000_04, lst_51000_02, lst_53000_02, lst_54100)]
		final_res = [a/b if a!=0 and b!=0 else 0 for a,b in zip(numeratr,lst_50000)]
		per_final_result = []
		for i in final_res:
			print(i)
			per_final_result.append('{:.2f}%'.format(i))
		return per_final_result


	def stores_and_repairs(filters):
		lst_54200 = get_monthly_gl_debit_no_opening("542%", filters)
		lst_54300 = get_monthly_gl_debit_no_opening("543%", filters)
		lst_50000 = get_monthly_gl_credit_no_opening("5%", filters)
		numeratr = [a+b for a,b in zip(lst_54200, lst_54300)]
		final_res = [a/b if a!=0 and b!=0 else 0 for a,b in zip(numeratr,lst_50000)]
		per_final_result = []
		for i in final_res:
			print(i)
			per_final_result.append('{:.2f}%'.format(i))
		return per_final_result


	def utilities(filters):
		lst_54400  = get_monthly_gl_debit_no_opening("544%", filters)
		lst_51000_05 = get_monthly_gl_debit_no_opening("51000-05", filters)
		lst_52000_04 = get_monthly_gl_debit_no_opening("52000-04", filters)
		lst_53000_04 = get_monthly_gl_debit_no_opening("53000-04", filters)
		lst_50000 = get_monthly_gl_credit_no_opening("5%", filters)
		numeratr = [a+b+c+d for a,b,c,d in zip(lst_54400, lst_51000_05,lst_52000_04,lst_53000_04)]
		final_res = [a/b if a!=0 and b!=0 else 0 for a,b in zip(numeratr,lst_50000)]
		per_final_result = []
		for i in final_res:
			print(i)
			per_final_result.append('{:.2f}%'.format(i))
		return per_final_result


	ut = utilities(filters)
	sr = stores_and_repairs(filters)
	mp = manpower_cost(filters)
	fu = fuel(filters)
	dm = direct_material(filters)
	month = ["Jan","Feb","Mar","April","May","June","July","Aug","Sept","Oct","Nov","Dec"]
	res = []
	for (i,j,k,l,m,n) in zip(month,dm,fu,mp,sr,ut):
		res.append([i,j,k,l,m,n])
	return res