# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from ethal.ethal.report.liquidity_ratios.liquidity_ratios import get_monthly_gl_credit,get_monthly_gl_credit_no_opening,get_monthly_gl_debit,get_monthly_gl_debit_no_opening,get_monthly_gl_credit_20000,get_monthly_gl_debit_10000

def execute(filters=None):
	columns, data = [], []
	data = get_data()
	columns = ["Month::180"]+["Gross Profit Margin::180"]+["Net Profit Margin::180"]+["EBITDA Margin::180"]+["EBIT Margin::180"]+["Return on Assets (ROA)::180"]+["Return on Equity/Investment::180"]
	return columns, data

def get_data():
	
	def gross_profit_margin():
		lst_41000 = get_monthly_gl_credit_no_opening("41%")
		lst_50000 = get_monthly_gl_debit_no_opening("5%")
		
		final_res = [(b-m) / b*100 if m != 0 and b!=0 else 0 for b,m in zip(lst_41000, lst_50000)]
		return final_res

	def net_profit_margin():
		lst_40000 = get_monthly_gl_credit_no_opening("4%")
		lst_50000 = get_monthly_gl_debit_no_opening("5%")
		lst_60000 = get_monthly_gl_debit_no_opening("6%")
		
		final_res = [(b-m-k) / b*100 if m != 0 and b!=0 else 0 for b,m,k in zip(lst_40000, lst_50000, lst_60000)]
		return final_res

	def EBITDA_margin():
		lst_40000 = get_monthly_gl_credit_no_opening("4%")
		lst_50000 = get_monthly_gl_debit_no_opening("5%")
		lst_60000 = get_monthly_gl_debit_no_opening("6%")
		lst_62000 = get_monthly_gl_debit_no_opening("62%")
		lst_63000_16 = get_monthly_gl_debit_no_opening("63000-16%")
		lst_41000 = get_monthly_gl_credit_no_opening("41%")
		numeratr = [a-b-c+d+e for a,b,c,d,e in zip(lst_40000, lst_50000, lst_60000, lst_62000, lst_63000_16)]
		final_res = [a / f*100 if a!=0 and f!=0 else 0 for a,f in zip(numeratr, lst_41000)]
		return final_res
	
	def EBIT_margin():
		lst_40000 = get_monthly_gl_credit_no_opening("4%")
		lst_50000 = get_monthly_gl_debit_no_opening("5%")
		lst_60000 = get_monthly_gl_debit_no_opening("6%")
		lst_62000 = get_monthly_gl_debit_no_opening("62%")
		lst_41000 = get_monthly_gl_credit_no_opening("41%")
		numeratr = [a-b-c+d for a,b,c,d in zip(lst_40000, lst_50000, lst_60000, lst_62000)]
		final_res = [a / f*100 if a!=0 and f!=0 else 0 for a,f in zip(numeratr, lst_41000)]
		return final_res

	def return_on_assets():
		lst_40000 = get_monthly_gl_credit_no_opening("4%")
		lst_50000 = get_monthly_gl_debit_no_opening("5%")
		lst_60000 = get_monthly_gl_debit_no_opening("6%")
		lst_10000 = get_monthly_gl_debit_10000("1%")
		numeratr = [a-b-c for a,b,c in zip(lst_40000, lst_50000, lst_60000)]
		final_res = [a / f*100 if a!=0 and f!=0 else 0 for a,f in zip(numeratr, lst_10000)]
		return final_res

	def return_on_equity():
		lst_40000_no = get_monthly_gl_credit_no_opening("4%")
		lst_50000_no = get_monthly_gl_debit_no_opening("5%")
		lst_60000_no = get_monthly_gl_debit_no_opening("6%")
		lst_40000 = get_monthly_gl_credit("4%")
		lst_50000 = get_monthly_gl_debit("5%")
		lst_60000 = get_monthly_gl_debit("6%")
		lst_30000 = get_monthly_gl_debit("3%")
		numeratr = [a-b-c for a,b,c in zip(lst_40000_no, lst_50000_no, lst_60000_no)]
		diff = [a-b-c for a,b,c in zip(lst_40000, lst_50000, lst_60000)]
		denominatr = [a+b for a,b in zip(lst_30000,diff)]
		final_res = [a / f*100 if a!=0 and f!=0 else 0 for a,f in zip(numeratr, denominatr)]
		return final_res

	roe = return_on_equity()
	roa = return_on_assets()
	ebm = EBIT_margin()
	em = EBITDA_margin()
	npm = net_profit_margin()
	gpm = gross_profit_margin()
	month = ["Jan","Feb","Mar","April","May","June","July","Aug","Sept","Oct","Nov","Dec"]
	res = []
	for (i,j,k,l,m,n,o) in zip(month,gpm,npm,em,ebm,roa,roe):
		res.append([i,j,k,l,m,n,o])
	return res