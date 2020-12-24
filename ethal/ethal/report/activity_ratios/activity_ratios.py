# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
# from ethal.ethal.report.liquidity_ratios.liquidity_ratios import get_monthly_gl_credit,get_monthly_gl_debit,get_monthly_gl_credit_20000,get_monthly_gl_debit_10000, get_monthly_gl_credit_no_opening, get_monthly_gl_debit_no_opening

def execute(filters=None):
	columns, data = [], []
	columns = ["Month::180"]+["Account Receivables Turnover::180"]+["Account Payables Turnover::180"]
	data = get_data()
	return columns, data

def account_receivable_turnover():
	return get_monthly_gl_debit('11200-01')

def get_monthly_gl_debit(account):
	a = frappe.db.sql("""select MONTH(posting_date) as month, sum(debit) from `tabGL Entry` where account like "{0}%" and (posting_date between '2020-02-01' and '2020-02-01') and YEAR(posting_date) = 2020 GROUP BY MONTH(posting_date) ORDER BY month;""".format(account), as_list=True)
	lst=[]
	for i in a:
		lst.append(i[0])
	
	for j in range(1,13):
		if j not in lst:
			a.append([j,0])
	a.sort()
	lst_a= []
	for i in a:
		lst_a.append(i[1])


	b = frappe.db.sql("""select MONTH(posting_date) as month, sum(credit) from `tabGL Entry` where account like "{0}%" and (posting_date between '2020-02-01' and '2020-02-01') and YEAR(posting_date) = 2020 GROUP BY MONTH(posting_date) ORDER BY month;""".format(account), as_list=True)
	lst_1=[]
	for i in b:
		lst_1.append(i[0])
	
	for j in range(1,13):
		if j not in lst_1:
			b.append([j,0])
	b.sort()
	lst_b= []
	for i in b:
		lst_b.append(i[1])

	res_a = [a-b for a,b in zip(lst_a,lst_b)]

	print("get_monthly_gl_debit ======> ",res_a)

	def add_one_by_one(l):
		new_l = []
		cumsum = 0
		for elt in l:
			cumsum += elt
			new_l.append(cumsum)
		return new_l

	fin = add_one_by_one(res_a)
	# print("opening and total added is =====> ", fin)
 
	fin_abs= []
	for i in fin:
		abs_val = abs(i)
		fin_abs.append(abs_val)
	print("opening and total added is =====> ", fin_abs)
	return fin_abs



def get_data():
	art = account_receivable_turnover()
	print(art)
