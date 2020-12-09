# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from ethal.ethal.report.liquidity_ratios.liquidity_ratios import get_monthly_gl_credit,get_monthly_gl_credit_no_opening,get_monthly_gl_debit,get_monthly_gl_debit_no_opening,get_monthly_gl_credit_20000,get_monthly_gl_debit_10000

def execute(filters=None):
	columns, data = [], []
	data = get_data()
	columns = ["Account::180"]+["Jan::120"]+["Feb::120"]+["Mar::120"]+["April::120"]+["May::120"]+["Jun::120"]+["July::120"]+["Aug::120"]+["Sept::120"]+["oct::120"]+["Nov::120"]+["Dec::120"]
	return columns, data

def add_one_by_one(l):
		new_l = []
		cumsum = 0
		for elt in l:
			cumsum -= elt
			new_l.append(cumsum)
		return new_l

def indirect_income():
	lst_42000 = get_monthly_gl_credit_no_opening("42")
	lst_42000.insert(0,"Indirect Income")
	fin = [lst_42000]
	return fin

def sales_net_of_taxes():
	lst_41000 = get_monthly_gl_credit_no_opening("41")
	lst_41000.insert(0,"Sales Net of Taxes")
	fin = [lst_41000]
	return fin

def stock_valuation_change_in_fg():
	lst_11510_11 = get_monthly_gl_debit("11510-11")
	lst_11520_02 = get_monthly_gl_debit("11520-02")
	final = [a+b for a,b in zip(lst_11510_11, lst_11520_02)]
	final_1 = [x - y for x, y in zip(final[:-1],final[1:])]
	final_1.insert(0,final[0])
	final_1.insert(0,"Stock Valuation Change in FG")
	fin = [final_1]
	return fin

def total_sales_net_of_taxes():
	l1 = indirect_income()
	for i in l1:
		l11 = i
	l11.pop(0)
	l2 = sales_net_of_taxes()
	for i in l2:
		l22 = i
	l22.pop(0)
	l3 = stock_valuation_change_in_fg()
	for i in l3:
		l33 = i
	l33.pop(0)
	final = [a+b+c for a,b,c in zip(l11,l22,l33)]
	final.insert(0,"Total Sales Net of Taxes")
	final = [final]
	return final

def power_consumed():
	lst_54400_01 = get_monthly_gl_debit_no_opening("54400-01")
	lst_54400_01.insert(0,"Power-Consumed")
	fin = [lst_54400_01]
	return fin

def consumables():
	lst_54200_06 = get_monthly_gl_debit_no_opening("54200-06")
	lst_54200_06.insert(0,"Consumables")
	fin = [lst_54200_06]
	return fin

def out_sourcing_costs():
	lst_51000_02 = get_monthly_gl_debit_no_opening("51000-02")
	lst_52000_04 = get_monthly_gl_debit_no_opening("52000-04")
	lst_53000_03 = get_monthly_gl_debit_no_opening("53000-03")
	lst_55000_01 = get_monthly_gl_debit_no_opening("55000-01")
	final = [a+b+c+d for a,b,c,d in zip(lst_51000_02,lst_52000_04,lst_53000_03,lst_55000_01)]
	final.insert(0,"Out Sourcing Cost")
	fin = [final]
	return fin

def packing_cost():
	lst_52000_03 = get_monthly_gl_debit_no_opening("52000-03")
	lst_52000_03.insert(0,"Packing Cost")
	fin = [lst_52000_03]
	return fin

def total_stores():
	lst_54200 = get_monthly_gl_debit_no_opening("542")
	lst_54200_06 = get_monthly_gl_debit_no_opening("54200-06")
	final = [a-b for a,b in zip(lst_54200,lst_54200_06)]
	final.insert(0,"stores")
	fin = [final]
	return fin

def fuel_diesel():
	lst_51000_03 = get_monthly_gl_debit_no_opening("51000-03")
	lst_51000_03.insert(0,"Fuel - Diesel")
	fin = [lst_51000_03]
	return fin

def raw_materials_consumed():
	lst_50000 = get_monthly_gl_debit_no_opening("5")
	lst_51000_02 = get_monthly_gl_debit_no_opening("51000-02")
	lst_52000_03 = get_monthly_gl_debit_no_opening("52000-03")
	lst_51000_03 = get_monthly_gl_debit_no_opening("51000-03")


	fin = [a-b-c-d for a,b,c,d in zip(lst_50000,lst_51000_02,lst_52000_03,lst_51000_03)]
	fin.insert(0,"Raw materials - Consumed")
	final = [fin]
	return final

def total_variable_cost():
	rmc = raw_materials_consumed()
	for i in rmc:
		rmc_1 = i
	rmc_1.pop(0)

	pc = power_consumed()
	for i in pc:
		pc_1 = i
	pc_1.pop(0)

	con = consumables()
	for i in con:
		con_1 = i
	con_1.pop(0)

	osc = out_sourcing_costs()
	for i in osc:
		osc_1 = i
	osc_1.pop(0)

	pac_cos = packing_cost()
	for i in pac_cos:
		pac_cos_1 = i
	pac_cos_1.pop(0)

	fd = fuel_diesel()
	for i in fd:
		fd_1 = i
	fd_1.pop(0)

	stores = total_stores()
	for i in stores:
		stores_1 = i
	stores_1.pop(0)

	fin = [a+b+c+d+e+f+j for a,b,c,d,e,f,j in zip(rmc_1,pc_1,con_1,osc_1,pac_cos_1,fd_1,stores_1)]
	fin.insert(0,"Total Variable Cost")
	final = [fin]
	return final

def throughput():
	tot1 = total_sales_net_of_taxes()
	for i in tot1:
		tot_1 = i
	tot_1.pop(0)

	tot2 = total_variable_cost()
	for i in tot2:
		tot_2 = i
	tot_2.pop(0)

	final = [a-b for a,b in zip(tot_1,tot_2)]
	final.insert(0,"Throughput")
	fin = [final]
	return fin

def operating_expenses():
	lst_54000 = get_monthly_gl_debit_no_opening("54")
	lst_60000 = get_monthly_gl_debit_no_opening("6")
	lst_62000 = get_monthly_gl_debit_no_opening("62")
	lst_54200 = get_monthly_gl_debit_no_opening("542")
	lst_54400_01 = get_monthly_gl_debit_no_opening("54400-01")
	lst_62000_03 = get_monthly_gl_debit_no_opening("62000-03")
	lst_62000_04 = get_monthly_gl_debit_no_opening("62000-04")
	lst_62000_05 = get_monthly_gl_debit_no_opening("62000-05")
	final = [(a+b)-c-d-e-f-g-h for a,b,c,d,e,f,g,h in zip(lst_54000,lst_60000,lst_62000,lst_54200,lst_54400_01,lst_62000_03,lst_62000_04,lst_62000_05)]
	final.insert(0,"Operating Expenses")
	fin = [final]
	return fin

def interest_count():
	lst_62000_03 = get_monthly_gl_debit_no_opening("62000-03")
	lst_62000_04 = get_monthly_gl_debit_no_opening("62000-04")
	lst_62000_05 = get_monthly_gl_debit_no_opening("62000-05")
	final = [a+b+c for a,b,c in zip(lst_62000_03,lst_62000_04,lst_62000_05)]
	final.insert(0,"Interest")
	fin = [final]
	return fin

def profit_before_taxes():
	tp = throughput()
	for i in tp:
		tp_1 = i
	tp_1.pop(0)

	oe = operating_expenses()
	for i in oe:
		oe_1 = i
	oe_1.pop(0)

	ic = interest_count()
	for i in ic:
		ic_1 = i
	ic_1.pop(0)

	final = [a-b-c for a,b,c in zip(tp_1,oe_1,ic_1)]
	final.insert(0,"Profit Before Taxes")
	fin = [final]
	return fin 

def profit_before_taxes_percentage():
	pbt = profit_before_taxes()
	for i in pbt:
		pbt_1 = i
	pbt_1.pop(0)

	snt = sales_net_of_taxes()
	for i in snt:
		snt_1 = i
	snt_1.pop(0)

	final = [(a/b)*100 if a!=0 and b!=0 else 0 for a,b in zip(pbt_1,snt_1)]
	final.insert(0,"Profit before taxes Percentage")
	fin = [final]
	return fin

def receivables_count():
	lst_11200 = get_monthly_gl_debit("112")
	# final_1 = [x - y for x, y in zip(lst_11200,lst_11200[1:])]
	# final_1.append(lst_11200[0])
	lst_11200.insert(0,"Receivables")
	fin = [lst_11200]
	return fin

def advance_to_supplier():
	lst_21000_01 = get_monthly_gl_credit("21000-01")
	# final_1 = [x - y for x, y in zip(lst_21000_01,lst_21000_01[1:])]
	# final_1.append(lst_21000_01[0])
	lst_21000_01.insert(0,"Advance to Supplier")
	fin = [lst_21000_01]
	return fin

def rm_count():
	lst_11510_01 = get_monthly_gl_debit("11510-01")
	lst_11510_05 = get_monthly_gl_debit("11510-05")
	lst_11510_06 = get_monthly_gl_debit("11510-06")
	final = [a+b+c for a,b,c in zip(lst_11510_01,lst_11510_05,lst_11510_06)]
	# final_1 = [x - y for x, y in zip(final,final[1:])]
	# final_1.append(final[0])
	final.insert(0,"RM")
	fin = [final]
	return fin

def wip_count():
	lst_11510_02 = get_monthly_gl_debit("11510-02")
	lst_11510_03 = get_monthly_gl_debit("11510-03")
	lst_11510_07 = get_monthly_gl_debit("11510-07")
	lst_11510_08 = get_monthly_gl_debit("11510-08")
	lst_11510_09 = get_monthly_gl_debit("11510-09")
	lst_11510_10 = get_monthly_gl_debit("11510-10")
	lst_11520_01 = get_monthly_gl_debit("11520-01")
	final = [a+b+c+d+e+f+g for a,b,c,d,e,f,g in zip(lst_11510_02,lst_11510_03,lst_11510_07,lst_11510_08,lst_11510_09,lst_11510_10,lst_11520_01)]
	# final_1 = [x - y for x, y in zip(final,final[1:])]
	# final_1.append(final[0])
	final.insert(0,"WIP")
	fin = [final]
	return fin

def fg_count():
	lst_11510_11 = get_monthly_gl_debit("11510-11")
	lst_11520_02 = get_monthly_gl_debit("11520-02")
	final = [a+b for a,b in zip(lst_11510_11,lst_11520_02)]
	# final_1 = [x - y for x, y in zip(final,final[1:])]
	# final_1.append(final[0])
	final.insert(0,"FG")
	fin = [final]
	return fin

def overdue_receivables():
	lst_11200 = get_monthly_gl_debit("112")
	lst = []
	for i in range(len(lst_11200)):
		if i == 0:
			lst.append(lst_11200[i])
		else:
			nb = sum(lst_11200[0:i+1]) - lst_11200[i]
			lst.append(nb)
	lst.insert(0,"Overdue Receivables")
	fin = [lst]
	return fin


def gross_working_capital():
	rc = receivables_count()
	for i in rc:
		rc_1 = i
	rc_1.pop(0)

	ats = advance_to_supplier()
	for i in ats:
		ats_1 = i
	ats_1.pop(0)

	rmc = rm_count()
	for i in rmc:
		rmc_1 = i
	rmc_1.pop(0)

	wipc = wip_count()
	for i in wipc:
		wipc_1 = i
	wipc_1.pop(0)

	fgc = fg_count()
	for i in fgc:
		fgc_1 = i
	fgc_1.pop(0)

	ovr = overdue_receivables()
	for i in ovr:
		ovr_1 = i
	ovr_1.pop(0)

	final = [(a+b+c+d+e+f) for a,b,c,d,e,f in zip(rc_1,ats_1,rmc_1,wipc_1,fgc_1,ovr_1)]
	final.insert(0,"Gross Working Capital")
	fin = [final]
	return fin

def total_payable():
	lst_21000_01 = get_monthly_gl_credit("21000-01")
	lst_21100 = get_monthly_gl_credit("211")
	lst_21300 = get_monthly_gl_credit("213")
	lst_21400 = get_monthly_gl_credit("214")

	final = [(a+b+c+d) for a,b,c,d in zip(lst_21000_01,lst_21100,lst_21300,lst_21400)]
	final.insert(0,"Total Payable (other than bank and cash)")
	fin = [final]
	return fin

def overdue_payable():
	tp = total_payable()
	for i in tp:
		tp_1 = i
	tp_1.pop(0)
	lst = []
	for i in range(len(tp_1)):
		if i == 0:
			lst.append(tp_1[i])
		else:
			nb = sum(tp_1[0:i+1]) - tp_1[i]
			lst.append(nb)
	lst.insert(0,"Overdue Payable")
	fin = [lst]
	return fin

def net_working_capital():
	gwc = gross_working_capital()
	for i in gwc:
		gwc_1 = i
	gwc_1.pop(0)

	tp = total_payable()
	for i in tp:
		tp_1 = i
	tp_1.pop(0)

	op = overdue_payable()
	for i in op:
		op_1 = i
	op_1.pop(0)
	
	final = [a-b-c for a,b,c in zip(gwc_1, tp_1, op_1)]
	final.insert(0,"Net Working Capital")
	fin = [final]
	return fin

def operational_free_cash_flow():
	pbt = profit_before_taxes()
	for i in pbt:
		pbt_1 = i
	pbt_1.pop(0)

	nwc = net_working_capital()
	for i in nwc:
		nwc_1 = i
	nwc_1.pop(0)

	final = [a+b for a,b in zip(pbt_1,nwc_1)]
	final.insert(0,"Operational Free Cash Flow (OFCF)")
	fin = [final]
	return fin

def operational_free_cash_score():
	ofcf = operational_free_cash_flow()
	for i in ofcf:
		ofcf_1 = i
	ofcf_1.pop(0)

	op = overdue_payable()
	for i in op:
		op_1 = i
	op_1.pop(0)

	final = [a-b for a,b in zip(ofcf_1, op_1)]
	final.insert(0,"Operational Free Cash Score")
	fin = [final]
	return fin

def capital_expenditure():
	lst_12000 = get_monthly_gl_debit_no_opening("12")
	lst_11700 = get_monthly_gl_debit_no_opening("117")
	lst_11410_01 = get_monthly_gl_debit_no_opening("11410-01")

	final = [a+b+c for a,b,c in zip(lst_12000,lst_11700,lst_11410_01)]
	final.insert(0,"Capital Expenditure")
	fin = [final]
	return fin

def working_capital_term_loan():
	lst_21200_02 = get_monthly_gl_credit_no_opening("21200-02")
	lst_21200_01 = get_monthly_gl_credit_no_opening("21200-01")
	lst_22100 = get_monthly_gl_credit_no_opening("221")

	final = [a+b+c for a,b,c in zip(lst_21200_02,lst_21200_01,lst_22100)]
	final.insert(0,"Working Capital Term Loan")
	fin = [final]
	return fin

def balance_in_bank_and_cash():
	lst_11100 = get_monthly_gl_debit_no_opening("111")
	lst_11100.insert(0,"Balance in Bank and Cash")
	fin = [lst_11100]
	return fin

def get_data():
	ii = indirect_income()
	snt = sales_net_of_taxes()
	svcf = stock_valuation_change_in_fg()
	tsnt = total_sales_net_of_taxes()
	pc = power_consumed()
	con = consumables()
	osc = out_sourcing_costs()
	pac_cos = packing_cost()
	strs = total_stores()
	fd = fuel_diesel()
	rmco = raw_materials_consumed()
	tvc = total_variable_cost()
	thp = throughput()
	oe = operating_expenses()
	ic = interest_count()
	pbt = profit_before_taxes()
	pbtp = profit_before_taxes_percentage()
	rc = receivables_count()
	ats = advance_to_supplier()
	rmc = rm_count()
	wipc = wip_count()
	fgc = fg_count()
	ovr = overdue_receivables()
	gwc = gross_working_capital()
	tp = total_payable()
	op = overdue_payable()
	nwc = net_working_capital()
	ofcf = operational_free_cash_flow()
	ofcr = operational_free_cash_score()
	ce = capital_expenditure()
	wctl = working_capital_term_loan()
	bibc = balance_in_bank_and_cash()

	return ii+snt+svcf+tsnt+pc+con+osc+pac_cos+strs+fd+rmco+tvc+thp+oe+ic+pbt+pbtp+gwc+rc+ats+rmc+wipc+fgc+ovr+tp+op+nwc+ofcf+ofcr+ce+wctl+bibc


	