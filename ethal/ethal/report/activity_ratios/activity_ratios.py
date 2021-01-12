# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from ethal.ethal.report.liquidity_ratios.liquidity_ratios import get_monthly_gl_credit,get_monthly_gl_debit,get_monthly_gl_credit_20000,get_monthly_gl_debit_10000, get_monthly_gl_credit_no_opening, get_monthly_gl_debit_no_opening

def execute(filters=None):
	columns, data = [], []
	columns = ["Month::180"]+["Account Receivables Turnover::180"]+["Account Payables Turnover::180"]
	data = get_data(filters)
	return columns, data

def get_1st_day_debit(account, filters):
		a = frappe.db.sql("""select MONTH(posting_date) as month, sum(debit) from `tabGL Entry` where account like "{0}%" and DATE_SUB(LAST_DAY(posting_date),INTERVAL DAY(LAST_DAY(posting_date))- 1 DAY) and YEAR(posting_date) = {1} GROUP BY MONTH(posting_date) ORDER BY month;""".format(account, filters['year']), as_list=True)
		# print("a", a)
		# month_list.append(a)
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


		b = frappe.db.sql("""select MONTH(posting_date) as month, sum(credit) from `tabGL Entry` where account like "{0}%" and DATE_SUB(LAST_DAY(posting_date),INTERVAL DAY(LAST_DAY(posting_date))- 1 DAY) and YEAR(posting_date) = {1} GROUP BY MONTH(posting_date) ORDER BY month;""".format(account, filters['year']), as_list=True)
		# print("b", b)
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

		# print("get_monthly_gl_debit ======> ",res_a)

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
		# print("opening and total added is =====> ", fin_abs)
		return fin_abs

def get_last_day_debit(account, filters):
	a = frappe.db.sql("""select MONTH(posting_date) as month, sum(debit) from `tabGL Entry` where account like "{0}%" and LAST_DAY(posting_date) and YEAR(posting_date) = {1} GROUP BY MONTH(posting_date) ORDER BY month;""".format(account, filters['year']), as_list=True)
	# print("a", a)
	# month_list.append(a)
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


	b = frappe.db.sql("""select MONTH(posting_date) as month, sum(credit) from `tabGL Entry` where account, like "{0}%" and LAST_DAY(posting_date) and YEAR(posting_date) = {1} GROUP BY MONTH(posting_date) ORDER BY month;""".format(account, filters['year']), as_list=True)
	# print("b", b)
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

	# print("get_monthly_gl_debit ======> ",res_a)

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
	# print("opening and total added is =====> ", fin_abs)
	return fin_abs	

def get_1st_day_credit(account, filters):
		a = frappe.db.sql("""select MONTH(posting_date) as month, sum(credit) from `tabGL Entry` where account like "{0}%" and DATE_SUB(LAST_DAY(posting_date),INTERVAL DAY(LAST_DAY(posting_date))- 1 DAY) and YEAR(posting_date) = {1} GROUP BY MONTH(posting_date) ORDER BY month;""".format(account, filters['year']), as_list=True)
		# print("a", a)
		# month_list.append(a)
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


		b = frappe.db.sql("""select MONTH(posting_date) as month, sum(debit) from `tabGL Entry` where account like "{0}%" and DATE_SUB(LAST_DAY(posting_date),INTERVAL DAY(LAST_DAY(posting_date))- 1 DAY) and YEAR(posting_date) = {1} GROUP BY MONTH(posting_date) ORDER BY month;""".format(account, filters['year']), as_list=True)
		# print("b", b)
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

		# print("get_monthly_gl_debit ======> ",res_a)

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
		# print("opening and total added is =====> ", fin_abs)
		return fin_abs

def get_last_day_credit(account, filters):
	a = frappe.db.sql("""select MONTH(posting_date) as month, sum(credit) from `tabGL Entry` where account like "{0}%" and LAST_DAY(posting_date) and YEAR(posting_date) = {1} GROUP BY MONTH(posting_date) ORDER BY month;""".format(account, filters['year']), as_list=True)
	# print("a", a)
	# month_list.append(a)
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


	b = frappe.db.sql("""select MONTH(posting_date) as month, sum(debit) from `tabGL Entry` where account like "{0}%" and LAST_DAY(posting_date) and YEAR(posting_date) = {1} GROUP BY MONTH(posting_date) ORDER BY month;""".format(account, filters['year']), as_list=True)
	# print("b", b)
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

	# print("get_monthly_gl_debit ======> ",res_a)

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
	# print("opening and total added is =====> ", fin_abs)
	return fin_abs	


def get_data(filters):

	def account_receivable_turnover(filters):
		return get_monthly_gl_debit('11200-01', filters)

	def account_payable_turnover(filters):
		return get_monthly_gl_credit('21000-01', filters)	

	def get_monthly_gl_debit(account, filters):
		first_day = get_1st_day_debit(account, filters)
		last_day = get_last_day_credit(account, filters)
		print(first_day)
		res_a = [(a+b)/2 for a,b in zip(first_day,last_day)]
		c = get_monthly_gl_credit_no_opening('41', filters)

		final_res = [a/b if a!=0 and b!=0 else 0 for a,b in zip(c,res_a)]
		per_final_result = []
		for i in final_res:
			per_final_result.append('{:.2f}%'.format(i))
		return per_final_result

	def get_monthly_gl_credit(account, filters):
		first_day = get_1st_day_credit(account, filters)
		last_day = get_last_day_credit(account, filters)

		res_a = [(a+b)/2 for a,b in zip(first_day,last_day)]
		c = get_monthly_gl_debit_no_opening('114', filters)

		final_res = [a/b if a!=0 and b!=0 else 0 for a,b in zip(c,res_a)]
		per_final_result = []
		for i in final_res:
			per_final_result.append('{:.2f}%'.format(i))
		return per_final_result	

	art = account_receivable_turnover(filters)
	apt = account_payable_turnover(filters)
	# print(art)
	month = ["Jan","Feb","Mar","April","May","June","July","Aug","Sept","Oct","Nov","Dec"]
	res = []
	for (i,j,k) in zip(month,art,apt):
		res.append([i,j,k])
	
	return res
