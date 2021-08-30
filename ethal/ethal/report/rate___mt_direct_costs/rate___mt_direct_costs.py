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
			"label": "Direct material/Total MT Sold",
			"fieldname": "direct_material",
			"fieldtype": "Currency",
			"width": 200
		},
		{
			"label": "Fuel/Total MT Sold",
			"fieldname": "fuel",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": "Manpower cost - factory/Total MT Sold",
			"fieldname": "manpower_cost",
			"fieldtype": "Currency",
			"width": 200
		},
		{
			"label": "Stores & repair costs /Total MT Sold",
			"fieldname": "stores",
			"fieldtype": "Currency",
			"width": 200
		},
			{
			"label": "Utilities cost/Total MT Sold",
			"fieldname": "utilities",
			"fieldtype": "Currency",
			"width": 200
		}
	]
	data = get_data(filters)
	return columns, data

def get_data(filters):

	def direct_material(filters):
		lst_51000_01 = get_monthly_gl_debit_no_opening("51000-01%", filters)
		lst_51000_02 = get_monthly_gl_debit_no_opening("51000-02%", filters)
		lst_52000_01 = get_monthly_gl_debit_no_opening("52000-01%", filters)
		lst_53000_01 = get_monthly_gl_debit_no_opening("53000-01%", filters)
		sales_invoice = sales_invoice_qty()
		final_res = [((a+b+c+d)/e[0]) if e[0]!=0 else 0 for a,b,c,d,e in zip(lst_51000_01, lst_51000_02, lst_52000_01, lst_53000_01, sales_invoice)]
		return final_res

	def fuel_mt_sold(filters):
		lst_51000_03 = get_monthly_gl_debit_no_opening("51000-03%", filters)
		sales_invoice = sales_invoice_qty()
		final_res = [(a/b[0]) if b[0]!=0 else 0 for a,b in zip(lst_51000_03, sales_invoice)]
		return final_res

	def manpower_cost(filters):
		lst_51000_04 = get_monthly_gl_debit_no_opening("51000-04%", filters)
		lst_52000_02 = get_monthly_gl_debit_no_opening("52000-02%", filters)
		lst_53000_02 = get_monthly_gl_debit_no_opening("53000-02%", filters)
		lst_54100 = get_monthly_gl_debit_no_opening("54100%", filters)
		sales_invoice = sales_invoice_qty()
		final_res = [((a+b+c+d)/e[0]) if e[0]!=0 else 0 for a,b,c,d,e in zip(lst_51000_04, lst_52000_02, lst_53000_02, lst_54100, sales_invoice)]
		return final_res

	def stores_repair_cost(filters):
		lst_54200 = get_monthly_gl_debit_no_opening("54200%", filters)
		lst_54300 = get_monthly_gl_debit_no_opening("54300%", filters)
		sales_invoice = sales_invoice_qty()
		final_res = [((a+b)/c[0]) if c[0]!=0 else 0 for a,b,c in zip(lst_54200, lst_54300, sales_invoice)]
		return final_res

	def utilities_cost(filters):
		lst_54400 = get_monthly_gl_debit_no_opening("54400%", filters)
		lst_51000_05 = get_monthly_gl_debit_no_opening("51000_05%", filters)
		lst_52000_04 = get_monthly_gl_debit_no_opening("52000_04%", filters)
		lst_53000_04 = get_monthly_gl_debit_no_opening("53000_04%", filters)
		sales_invoice = sales_invoice_qty()
		final_res = [((a+b+c+d)/e[0]) if e[0]!=0 else 0 for a,b,c,d,e in zip(lst_54400, lst_51000_05, lst_52000_04, lst_53000_04, sales_invoice)]
		return final_res

	direct = direct_material(filters)
	fuel = fuel_mt_sold(filters)
	manpower = manpower_cost(filters)
	stores = stores_repair_cost(filters)
	utilities = utilities_cost(filters)
	month = ["Jan","Feb","Mar","April","May","June","July","Aug","Sept","Oct","Nov","Dec"]
	res = []
	for (i,j,k,l,m,n) in zip(month,direct,fuel,manpower,stores,utilities):
		res.append([i,j,k,l,m,n])
	
	return res