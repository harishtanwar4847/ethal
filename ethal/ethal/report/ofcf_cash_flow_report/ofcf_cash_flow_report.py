## Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	data = get_data(filters)
	columns = ["Account::180"]+["Jan::120"]+["Feb::120"]+["Mar::120"]+["April::120"]+["May::120"]+["Jun::120"]+["July::120"]+["Aug::120"]+["Sept::120"]+["oct::120"]+["Nov::120"]+["Dec::120"]
	return columns, data

def add_one_by_one(l):
		new_l = []
		cumsum = 0
		for elt in l:
			cumsum -= elt
			new_l.append(cumsum)
		return new_l

def indirect_income(filters):
	lst_42000 = get_monthly_gl_credit_no_opening("42", filters)
	lst_42000.insert(0,"Other Income/Indirect Income")
	fin = [lst_42000]
	return fin

def utilities(filters):
	lst_52340 = get_monthly_gl_debit_no_opening("52340", filters)
	lst_53340 = get_monthly_gl_debit_no_opening("53340", filters)
	lst_51340 = get_monthly_gl_debit_no_opening("51340", filters)
	lst_54340 = get_monthly_gl_debit_no_opening("54340", filters)
	final = [a+b+c+d for a,b,c,d in zip(lst_52340,lst_53340,lst_51340,lst_54340)]
	
	final.insert(0,"Utilities- Power and Water")
	fin = [final]
	return fin

def raw_material_purchase(filters):
	lst_51000 = get_monthly_gl_debit_no_opening("51000-01", filters)
	lst_52000 = get_monthly_gl_debit_no_opening("52000-01", filters)
	lst_53000 = get_monthly_gl_debit_no_opening("53000-01", filters)
	lst_54000 = get_monthly_gl_debit_no_opening("54000-01", filters)
	final = [a+b+c+d for a,b,c,d in zip(lst_51000,lst_52000,lst_53000,lst_54000)]
	final.insert(0,"Raw materials purchase ")
	fin = [final]
	return fin

def depreciation(filters):
	lst_53200 = get_monthly_gl_debit_no_opening("53200-01", filters)
	lst_52200 = get_monthly_gl_debit_no_opening("52200-01", filters)

	print("lst_53200",lst_53200)
	print("lst_52200",lst_52200)

	final = [a+b for a,b in zip(lst_53200,lst_52200)]
	final.insert(0,"Depreciation")
	fin = [final]
	return fin

def store_repair_machinery_rent(filters):
	lst_52320 = get_monthly_gl_debit_no_opening("52320", filters)
	lst_52330 = get_monthly_gl_debit_no_opening("52330", filters)
	lst_53320 = get_monthly_gl_debit_no_opening("53320", filters)
	lst_53330 = get_monthly_gl_debit_no_opening("53330", filters)
	lst_54320 = get_monthly_gl_debit_no_opening("54320", filters)
	lst_54330 = get_monthly_gl_debit_no_opening("54330", filters)
	final = [a+b+c+d+e+f for a,b,c,d,e,f in zip(lst_52320,lst_52330,lst_53320,lst_53330,lst_54320,lst_54330)]
	final.insert(0,"Stores & Repair, Machinery rent")
	fin = [final]
	return fin

def manpower_cost(filters):
	lst_51100 = get_monthly_gl_debit_no_opening("51100",filters)
	lst_52100 = get_monthly_gl_debit_no_opening("52100", filters)
	lst_53100 = get_monthly_gl_debit_no_opening("53100", filters)
	lst_54100 = get_monthly_gl_debit_no_opening("54100", filters)
	lst_51310 = get_monthly_gl_debit_no_opening("51310", filters)
	lst_52310 = get_monthly_gl_debit_no_opening("52310", filters)
	lst_53210 = get_monthly_gl_debit_no_opening("53210", filters)
	lst_54310 = get_monthly_gl_debit_no_opening("54310", filters)


	final = [a+b+c+d+e+f+g+h for a,b,c,d,e,f,g,h in zip(lst_51100,lst_52100,lst_53100,lst_54100,lst_51310,lst_52310,lst_53210,lst_54310)]
	final.insert(0,"Manpower Cost")
	fin = [final]
	return fin
	
def sales_net_of_taxes(filters):
	lst_41000 = get_monthly_gl_credit_no_opening("41", filters)
	lst_41000.insert(0,"Sales Net of Taxes")
	fin = [lst_41000]
	return fin

def stock_valuation_change_in_fg(filters):
	lst_11510_11 = get_monthly_gl_debit("11510-03", filters)
	lst_11520_02 = get_monthly_gl_debit("11520-02", filters)
	lst_11530_02 = get_monthly_gl_debit("11530-02", filters)
	final = [a+b+c for a,b,c in zip(lst_11510_11, lst_11520_02, lst_11530_02)]
	final_1 = [x - y for x, y in zip(final[:-1],final[1:])]
	final_1.insert(0,final[0])
	final_1.insert(0,"Stock Valuation Change in FG")
	fin = [final_1]
	return fin

def total_sales_net_of_taxes(filters):
	l1 = indirect_income(filters)
	for i in l1:
		l11 = i
	l11.pop(0)
	l2 = sales_net_of_taxes(filters)
	for i in l2:
		l22 = i
	l22.pop(0)
	l3 = stock_valuation_change_in_fg(filters)
	for i in l3:
		l33 = i
	l33.pop(0)
	final = [a+b+c for a,b,c in zip(l11,l22,l33)]
	final.insert(0,"Total Sales Net of Taxes")
	final = [final]
	return final

def total_variable_cost(filters):
	l1 = raw_material_purchase(filters)
	for i in l1:
		l11 = i
	l11.pop(0)
	l2 = manpower_cost(filters)
	for i in l2:
		l22 = i
	l22.pop(0)
	l3 = utilities(filters)
	for i in l3:
		l33 = i
	l33.pop(0)
	l4 = store_repair_machinery_rent(filters)
	for i in l4:
		l44 = i
	l44.pop(0)
	l5 = depreciation(filters)
	for i in l5:
		l55 = i
	l55.pop(0)

	final = [a+b+c+d+e for a,b,c,d,e in zip(l11,l22,l33,l44,l55)]
	final.insert(0,"Total Variable cost (TVC)")
	final = [final]
	return final

def pre_rm_to_sale(filters):
	l1 = raw_material_purchase(filters)
	for i in l1:
		l11 = i
	l11.pop(0)
	l2 = sales_net_of_taxes(filters)
	for i in l2:
		l22 = i
	l22.pop(0)
	
	final = [(a/b)*100 if a!=0 and b!=0 else 0 for a,b in zip(l11,l22)]
	final.insert(0,"% RM to Sale")
	final = [final]
	return final

def throughput(filters):
	tot1 = total_sales_net_of_taxes(filters)
	for i in tot1:
		tot_1 = i
	tot_1.pop(0)

	tot2 = total_variable_cost(filters)
	for i in tot2:
		tot_2 = i
	tot_2.pop(0)

	final = [a-b for a,b in zip(tot_1,tot_2)]
	final.insert(0,"Throughput")
	fin = [final]
	return fin

def operating_expenses(filters):
	lst_54000 = get_monthly_gl_debit_no_opening("54", filters)
	lst_60000 = get_monthly_gl_debit_no_opening("6", filters)
	lst_62000 = get_monthly_gl_debit_no_opening("62", filters)
	lst_54200 = get_monthly_gl_debit_no_opening("542", filters)
	lst_54400_01 = get_monthly_gl_debit_no_opening("54400-01", filters)
	lst_62000_03 = get_monthly_gl_debit_no_opening("62000-03", filters)
	lst_62000_04 = get_monthly_gl_debit_no_opening("62000-04", filters)
	lst_62000_05 = get_monthly_gl_debit_no_opening("62000-05", filters)
	final = [(a+b)-c-d-e-f-g-h for a,b,c,d,e,f,g,h in zip(lst_54000,lst_60000,lst_62000,lst_54200,lst_54400_01,lst_62000_03,lst_62000_04,lst_62000_05)]
	final.insert(0,"Operating Expenses")
	fin = [final]
	return fin

def interest_count(filters):
	lst_21200_04 = get_monthly_gl_credit_no_opening("21200-04", filters)
	lst_21200_05 = get_monthly_gl_credit_no_opening("21200-05", filters)
	lst_22100_02 = get_monthly_gl_credit_no_opening("22100-02", filters)
	final = [a+b+c for a,b,c in zip(lst_21200_04,lst_21200_05,lst_22100_02)]
	final.insert(0,"Interest")
	fin = [final]
	return fin

def profit_before_taxes(filters):
	tp = throughput(filters)
	for i in tp:
		tp_1 = i
	tp_1.pop(0)

	oe = operating_expenses(filters)
	for i in oe:
		oe_1 = i
	oe_1.pop(0)

	ic = interest_count(filters)
	for i in ic:
		ic_1 = i
	ic_1.pop(0)

	final = [a-b-c for a,b,c in zip(tp_1,oe_1,ic_1)]
	final.insert(0,"Profit Before Taxes")
	fin = [final]
	return fin 

def profit_before_taxes_percentage(filters):
	pbt = profit_before_taxes(filters)
	for i in pbt:
		pbt_1 = i
	pbt_1.pop(0)

	snt = sales_net_of_taxes(filters)
	for i in snt:
		snt_1 = i
	snt_1.pop(0)

	final = [(a/b)*100 if a!=0 and b!=0 else 0 for a,b in zip(pbt_1,snt_1)]
	final.insert(0,"Profit before taxes Percentage")
	fin = [final]
	return fin



def customer_advance(filters):
	lst_11200_01 = get_monthly_gl_credit("11200-01", filters)
	lst_11200_01.insert(0,"Advance (Debtors-Customer Advances)")
	fin = [lst_11200_01]
	return fin

def advance_other(filters):
	lst_11200_02 = get_monthly_gl_debit("11200-02", filters)
	lst_11200_03 = get_monthly_gl_debit	("11200-03", filters)
	lst_11200_04 = get_monthly_gl_debit	("11200-04", filters)
	lst_11200_05 = get_monthly_gl_debit	("11200-05", filters)
	lst_11200_06 = get_monthly_gl_debit	("11200-06", filters)
	lst_11210 = get_monthly_gl_debit	("11210", filters)
	lst_11220 = get_monthly_gl_debit	("11220", filters)
	lst_11230 = get_monthly_gl_debit	("11231", filters)
	lst_11600 = get_monthly_gl_debit	("1160", filters)

	final = [a+b+c+d+e+f+g+h+i for a,b,c,d,e,f,g,h,i in zip(lst_11200_02,lst_11200_03,lst_11200_04,lst_11200_05,lst_11200_06,lst_11210,lst_11220,lst_11230,lst_11600)]
	final.insert(0,"Advance Other")
	fin = [final]
	return fin

def inventory(filters):
	lst_11420 = get_monthly_gl_debit_no_opening("11420", filters)
	lst_11420.insert(0,"Inventory")
	fin = [lst_11420]
	return fin

def stock_in_hand(filters):
	lst_11510 = get_monthly_gl_debit_no_opening("11510", filters)
	lst_11520 = get_monthly_gl_debit_no_opening("11520", filters)
	
	final = [a+b for a,b in zip(lst_11510,lst_11520)]
	final.insert(0,"Stock In Hand")
	fin = [final]
	return fin


def overdue_receivables(filters):
	# lst_11300_01 = get_monthly_gl_debit("11300_01", filters)
	# lst_11300_02 = get_monthly_gl_debit("11510-02", filters)
	# lst_11300_03 = get_monthly_gl_debit_no_opening("11510-03", filters)
	# final = [a+b+c for a,b,c in zip(lst_11300_01,lst_11300_02,lst_11300_03)]
	# final.insert(0,"Overdue Receivables")
	# fin = [final]
	# return fin
	lst_11200_01 = get_monthly_gl_debit("11200-01", filters)
	lst_11200_01.insert(0,"Overdue Receivables")
	fin = [lst_11200_01]
	return fin



def get_monthly_gl_credit(account, filters):
		a = frappe.db.sql("""select MONTH(posting_date) as month, sum(credit) 
		from `tabGL Entry` where account like "{0}%" 
		and YEAR(posting_date) = {1} GROUP BY MONTH(posting_date) ORDER BY month;""".format(account, filters['year']), as_list=True)
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
		and YEAR(posting_date) = {1} GROUP BY MONTH(posting_date) ORDER BY month;""".format(account, filters['year']), as_list=True)
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

def get_monthly_gl_debit(account, filters):
	a = frappe.db.sql("""select MONTH(posting_date) as month, sum(debit) 
	from `tabGL Entry` where account like "{0}%" 
	and YEAR(posting_date) = {1} GROUP BY MONTH(posting_date) ORDER BY month;""".format(account, filters['year']), as_list=True)
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
	and YEAR(posting_date) = {1} GROUP BY MONTH(posting_date) ORDER BY month;""".format(account, filters['year']), as_list=True)
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

def get_monthly_gl_credit_no_opening(account, filters):
	
	a = frappe.db.sql("""select MONTH(posting_date) as month, sum(credit) 
	from `tabGL Entry` where account like "{0}%" and YEAR(posting_date) = {1} GROUP BY MONTH(posting_date) ORDER BY month;""".format(account, filters['year']), as_list=True)
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
	and YEAR(posting_date) = {1} GROUP BY MONTH(posting_date) ORDER BY month;""".format(account, filters['year']), as_list=True)
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


def get_monthly_gl_debit_no_opening(account,filters):
	a = frappe.db.sql("""select MONTH(posting_date) as month, sum(debit) 
	from `tabGL Entry` where account like "{0}%" 
	and YEAR(posting_date) = {1} GROUP BY MONTH(posting_date) ORDER BY month;""".format(account, filters['year']), as_list=True)
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
	and YEAR(posting_date) = {1} GROUP BY MONTH(posting_date) ORDER BY month;""".format(account, filters['year']), as_list=True)

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

	fin = res_a

	fin_abs= []
	for i in fin:
		abs_val = abs(i)
		fin_abs.append(abs_val)

	return fin_abs

def gross_working_capital(filters):
	rc = customer_advance(filters)
	for i in rc:
		rc_1 = i
	rc_1.pop(0)

	ats = advance_other(filters)
	for i in ats:
		ats_1 = i
	ats_1.pop(0)

	rmc = inventory(filters)
	for i in rmc:
		rmc_1 = i
	rmc_1.pop(0)

	wipc = overdue_receivables(filters)
	for i in wipc:
		wipc_1 = i
	wipc_1.pop(0)


	final = [(a+b+c+d) for a,b,c,d in zip(rc_1,ats_1,rmc_1,wipc_1)]
	final.insert(0,"Gross Working Capital")
	fin = [final]
	return fin

def total_payable(filters):
	lst_21200 = get_monthly_gl_credit("212", filters)
	lst_21100 = get_monthly_gl_credit("211", filters)
	lst_21300 = get_monthly_gl_credit("213", filters)
	lst_21400 = get_monthly_gl_credit("214", filters)
	lst_22200 = get_monthly_gl_credit("22200", filters)

	final = [(a+b+c+d)-(e) for a,b,c,d,e in zip(lst_21200,lst_21100,lst_21300,lst_21400,lst_22200)]
	final.insert(0,"Total Payable (other than bank and cash)")
	fin = [final]
	return fin

def overdue_payable(filters):
	lst_22200 = get_monthly_gl_credit("222", filters)
	lst_21300 = get_monthly_gl_credit("213", filters)

	final = [(a+b) for a,b in zip(lst_21300,lst_22200)]
	final.insert(0,"Overdue payables")
	fin = [final]
	return fin

def net_working_capital(filters):
	gwc = gross_working_capital(filters)
	for i in gwc:
		gwc_1 = i
	gwc_1.pop(0)

	tp = total_payable(filters)
	for i in tp:
		tp_1 = i
	tp_1.pop(0)

	
	final = [a-b for a,b in zip(gwc_1, tp_1)]
	final.insert(0,"Net Working Capital")
	fin = [final]
	return fin

def operational_free_cash_flow(filters):
	pbt = profit_before_taxes(filters)
	for i in pbt:
		pbt_1 = i
	pbt_1.pop(0)

	nwc = net_working_capital(filters)
	for i in nwc:
		nwc_1 = i
	nwc_1.pop(0)

	final = [a+b for a,b in zip(pbt_1,nwc_1)]
	final.insert(0,"Operational Free Cash Flow (OFCF)")
	fin = [final]
	return fin

def operational_free_cash_score(filters):
	ofcf = operational_free_cash_flow(filters)
	for i in ofcf:
		ofcf_1 = i
	ofcf_1.pop(0)

	op = overdue_payable(filters)
	for i in op:
		op_1 = i
	op_1.pop(0)

	final = [a-b for a,b in zip(ofcf_1, op_1)]
	final.insert(0,"Operational Free Cash Score")
	fin = [final]
	return fin

def capital_expenditure(filters):
	lst_11300_04 = get_monthly_gl_debit_no_opening("11300-04", filters)
	lst_11700 = get_monthly_gl_debit_no_opening("117", filters)
	lst_11410 = get_monthly_gl_debit_no_opening("11410", filters)
	lst_12100 = get_monthly_gl_debit_no_opening("12100", filters)
	lst_12200 = get_monthly_gl_debit_no_opening("12200", filters)
	lst_12300 = get_monthly_gl_debit_no_opening("12300", filters)
	lst_supense = get_monthly_gl_debit_no_opening("Suspense", filters)

	final = [a+b+c+d+e+f+g for a,b,c,d,e,f,g in zip(lst_11300_04,lst_11700,lst_11410,lst_12100,lst_12200,lst_12300,lst_supense)]
	final.insert(0,"Capital Expenditure")
	fin = [final]
	return fin

def working_capital_term_loan(filters):
	lst_21200_01 = get_monthly_gl_credit_no_opening("21200-01",filters)
	lst_21100 = get_monthly_gl_credit_no_opening("21100",filters)

	final = [a+b for a,b in zip(lst_21200_01,lst_21200_01)]
	final.insert(0,"Working Capital Term Loan")
	fin = [final]
	return fin

def balance_in_bank_and_cash(filters):
	lst_11100 = get_monthly_gl_debit_no_opening("111", filters)
	lst_11100.insert(0,"Balance in Bank and Cash")
	fin = [lst_11100]
	return fin

def get_data(filters):
	snt = sales_net_of_taxes(filters)
	svcf = stock_valuation_change_in_fg(filters)
	ii = indirect_income(filters)
	tsnt = total_sales_net_of_taxes(filters)
	tvc = total_variable_cost(filters)
	prts = pre_rm_to_sale(filters)
	rmp = raw_material_purchase(filters)
	mc = manpower_cost(filters)
	ut = utilities(filters)
	srmr = store_repair_machinery_rent(filters)
	dp = depreciation(filters)
	thp = throughput(filters)
	oe = operating_expenses(filters)
	ic = interest_count(filters)
	pbt = profit_before_taxes(filters)
	pbtp = profit_before_taxes_percentage(filters)
	gwc = gross_working_capital(filters)
	ca = customer_advance(filters)
	ao = advance_other(filters)
	iv = inventory(filters)
	sih = stock_in_hand(filters)
	ovr = overdue_receivables(filters)
	tp = total_payable(filters)
	op = overdue_payable(filters)
	nwc = net_working_capital(filters)
	ofcf = operational_free_cash_flow(filters)
	ofcr = operational_free_cash_score(filters)
	ce = capital_expenditure(filters)
	wctl = working_capital_term_loan(filters)
	bibc = balance_in_bank_and_cash(filters)
	
	
	return snt+svcf+ii+tsnt+tvc+prts+rmp+mc+ut+srmr+dp+thp+oe+ic+pbt+pbtp+gwc+ca+ao+iv+sih+ovr+tp+op+nwc+ofcf+ofcr+ce+wctl+bibc


	
