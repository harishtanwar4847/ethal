# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	data = get_data()
	columns = ["Month::180"]+["Current/working Capital::180"]+["Quick(Acid)::180"]
	return columns, data

def get_data():
	
	def get_current_working_capital():
		
		lst_11000 = get_monthly_gl_debit("11")
		print("lst_11000 ====> ", lst_11000)
		lst_21000 = get_monthly_gl_credit_20000("21")
		print("lst_21000 ====> ", lst_21000)

		final = [b / m if m != 0 and b!=0 else 0 for b,m in zip(lst_11000, lst_21000)]
		return final

	def total_current_asset():
		lst_11000 = get_monthly_gl_debit("11")
		lst_11500 = get_monthly_gl_debit("115")

		final = [b - m for b,m in zip(lst_11000, lst_11500)]
		return final

	def total_current_liability():
		lst_21000 = get_monthly_gl_credit_20000("21")
		lst_21500 = get_monthly_gl_credit_20000("215")
		final = [b - m for b,m in zip(lst_21000, lst_21500)]
		return final

	
	cwc = get_current_working_capital()	
	tca = total_current_asset()
	tcl = total_current_liability()
	quick = [b / m if m != 0 and b!=0 else 0 for b,m in zip(tca, tcl)]
	month = ["Jan","Feb","Mar","April","May","June","July","Aug","Sept","Oct","Nov","Dec"]
	res = []
	for (i,j,m) in zip(month,cwc,quick):
		res.append([i,j,m])
	
	print("res ======> ",res)

	return res

def get_monthly_gl_credit(account):
		a = frappe.db.sql("""select MONTH(posting_date) as month, sum(credit) 
		from `tabGL Entry` where account like "{0}%" 
		and YEAR(posting_date) = year(curdate()) GROUP BY MONTH(posting_date) ORDER BY month;""".format(account), as_list=True)
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

		b = frappe.db.sql("""select MONTH(posting_date) as month, sum(debit) 
		from `tabGL Entry` where account like "{0}%" 
		and YEAR(posting_date) = year(curdate()) GROUP BY MONTH(posting_date) ORDER BY month;""".format(account), as_list=True)
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
		# print("get_monthly_gl_credit ======> ",res_a)

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

		return fin_abs


def get_monthly_gl_credit_no_opening(account):
		a = frappe.db.sql("""select MONTH(posting_date) as month, sum(credit) 
		from `tabGL Entry` where account like "{0}%" 
		and YEAR(posting_date) = year(curdate()) GROUP BY MONTH(posting_date) ORDER BY month;""".format(account), as_list=True)
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

		b = frappe.db.sql("""select MONTH(posting_date) as month, sum(debit) 
		from `tabGL Entry` where account like "{0}%" 
		and YEAR(posting_date) = year(curdate()) GROUP BY MONTH(posting_date) ORDER BY month;""".format(account), as_list=True)
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
		# print("get_monthly_gl_credit ======> ",res_a)

		fin = res_a
		# print("opening and total added is =====> ", fin)

		fin_abs= []
		for i in fin:
			abs_val = abs(i)
			fin_abs.append(abs_val)

		return fin_abs


def get_monthly_gl_debit(account):
	a = frappe.db.sql("""select MONTH(posting_date) as month, sum(debit) 
	from `tabGL Entry` where account like "{0}%" 
	and YEAR(posting_date) = year(curdate()) GROUP BY MONTH(posting_date) ORDER BY month;""".format(account), as_list=True)
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


	b = frappe.db.sql("""select MONTH(posting_date) as month, sum(credit) 
	from `tabGL Entry` where account like "{0}%" 
	and YEAR(posting_date) = year(curdate()) GROUP BY MONTH(posting_date) ORDER BY month;""".format(account), as_list=True)
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

	return fin_abs


def get_monthly_gl_debit_no_opening(account):
	a = frappe.db.sql("""select MONTH(posting_date) as month, sum(debit) 
	from `tabGL Entry` where account like "{0}%" 
	and YEAR(posting_date) = year(curdate()) GROUP BY MONTH(posting_date) ORDER BY month;""".format(account), as_list=True)
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


	b = frappe.db.sql("""select MONTH(posting_date) as month, sum(credit) 
	from `tabGL Entry` where account like "{0}%" 
	and YEAR(posting_date) = year(curdate()) GROUP BY MONTH(posting_date) ORDER BY month;""".format(account), as_list=True)
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

	fin = res_a
	# print("opening and total added is =====> ", fin)

	fin_abs= []
	for i in fin:
		abs_val = abs(i)
		fin_abs.append(abs_val)

	return fin_abs


def get_monthly_gl_credit_20000(account):
	a = frappe.db.sql("""select MONTH(posting_date) as month, sum(credit) 
	from `tabGL Entry` where account like "{0}%"
	or account = "Asset Received But Not Billed - ETL" or account = "Stock Received But Not Billed - ETL" 
	and YEAR(posting_date) = year(curdate()) GROUP BY MONTH(posting_date) ORDER BY month;""".format(account), as_list=True)
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

	b = frappe.db.sql("""select MONTH(posting_date) as month, sum(debit)
	from `tabGL Entry` where account like "{0}%" or account = "Asset Received But Not Billed - ETL" 
	or account = "Stock Received But Not Billed - ETL" 
	and YEAR(posting_date) = year(curdate()) GROUP BY MONTH(posting_date) ORDER BY month;""".format(account), as_list=True)
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

	# print("get_monthly_gl_credit_20000 ======> ",res_a)

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

	return fin_abs

def get_monthly_gl_debit_10000(account):
	a = frappe.db.sql("""select MONTH(posting_date) as month, sum(debit)
	 from `tabGL Entry` where account like "{0}%" or account = "Round off account - ETL" or account = "Temporary Opening - ETL"
	  and YEAR(posting_date) = year(curdate()) GROUP BY MONTH(posting_date) ORDER BY month;""".format(account), as_list=True)
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

	print('debit', lst_a)
	b = frappe.db.sql("""select MONTH(posting_date) as month, sum(credit)
	 from `tabGL Entry` where account like "{0}%" or account = "Round off account - ETL" or account = "Temporary Opening - ETL" 
	 and YEAR(posting_date) = year(curdate()) GROUP BY MONTH(posting_date) ORDER BY month;""".format(account), as_list=True)
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
	print('credit', lst_b)
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

	return fin_abs