# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from ethal.ethal.report.liquidity_ratios.liquidity_ratios import get_monthly_gl_credit,get_monthly_gl_debit,get_monthly_gl_credit_20000,get_monthly_gl_debit_10000

def execute(filters=None):
	columns, data = [], []
	data = get_data()
	columns = ["Month::180"]+["Debts to Assets::180"]+["Debts to Equity::180"]
	return columns, data

def get_data():
	def debts_to_assets():
		lst_10000 = get_monthly_gl_debit_10000("1")
		print("lst_10000 ====> ", lst_10000)
		lst_20000 = get_monthly_gl_credit_20000("2")
		print("lst_20000 ====> ", lst_20000)

		final = [(b / m)*100 if m != 0 and b!=0 else 0 for b,m in zip(lst_20000,lst_10000)]
		return final
	
	def debts_to_equity():
		lst_20000 = get_monthly_gl_credit_20000("2")
		lst_30000 = get_monthly_gl_debit("3")
		lst_40000 = get_monthly_gl_debit("4")
		lst_50000 = get_monthly_gl_debit("5")
		lst_60000 = get_monthly_gl_debit("6")

		deno = [(a+(b-c-d)) for a,b,c,d in zip(lst_30000,lst_40000,lst_50000,lst_60000)]
		final = [(a/b)*100 if a!= 0 and b!=0 else 0 for a,b in zip(lst_20000,deno)]
		return final


	

	# total_liability_10000 = total_liability_10000()
	# total_equity = total_equity()
	dta = debts_to_assets()	
	debts_to_equity = debts_to_equity() 
	month = ["Jan","Feb","Mar","April","May","June","July","Aug","Sept","Oct","Nov","Dec"]
	res = []
	for (i,j,k) in zip(month,dta,debts_to_equity):
		res.append([i,j,k])
	
	return res