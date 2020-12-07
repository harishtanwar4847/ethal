# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from ethal.ethal.report.liquidity_ratios.liquidity_ratios import get_monthly_gl_credit,get_monthly_gl_credit_no_opening,get_monthly_gl_debit,get_monthly_gl_debit_no_opening,get_monthly_gl_credit_20000,get_monthly_gl_debit_10000

def execute(filters=None):
	columns, data = [], []
	columns = ["Month::180"]+["DB sales % ::180"]+["TU sales % ::180"]
	data = get_data()
	return columns, data

def get_data():
	
	def db_sales_percent():
		lst_41110 = get_monthly_gl_credit_no_opening("4111%")
		lst_41100 = get_monthly_gl_credit_no_opening("411%")
		final_res = [a / f*100 if a!=0 and f!=0 else 0 for a,f in zip(lst_41110, lst_41100)]
		return final_res

	def tu_sales_percent():
		lst_41120 = get_monthly_gl_credit_no_opening("4112%")
		lst_41100 = get_monthly_gl_credit_no_opening("411%")
		final_res = [a / f*100 if a!=0 and f!=0 else 0 for a,f in zip(lst_41120, lst_41100)]
		return final_res

	dsp = db_sales_percent()
	tsp = tu_sales_percent()
	month = ["Jan","Feb","Mar","April","May","June","July","Aug","Sept","Oct","Nov","Dec"]
	res = []
	for (i,j,k) in zip(month,dsp,tsp):
		res.append([i,j,k])
	return res