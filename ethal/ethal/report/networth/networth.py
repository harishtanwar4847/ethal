# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import pprint 
from datetime import datetime

def execute(filters=None):
	columns, data = [], []
	data = get_data(filters)
	columns = ["Account::280"]+["Amount::300"]
	return columns, data

def assets():
	return {'Account': 'Assets:', 'Amount': '', 'indent': 0}

def fixed_assets_gross_block(filters):
	return calculate_amount_of_accounts_of_debit(filters, 'Fixed Assets - Gross Block', '121', indent=1)

def stock_value_market_price(filters):
	return calculate_amount_of_accounts_of_debit(filters, 'Stock value ( Market price)', '115',indent=1,)

def cash_and_bank_account(filters):
	return calculate_amount_of_accounts_of_debit(filters, 'Cash &  Bank', '111', indent=1)

def advances(filters):
	return {'Account': 'Advances', 'Amount': '', 'indent': 1}

def debtors_customer_advances(filters):
	return calculate_amount_of_accounts_of_debit(filters, '(Debtors + Customer Advances)', '112', indent=2)
	
def des_general(filters):
	return calculate_amount_of_accounts_of_advance(filters, 'Des General ', indent=2)

def des_industries(filters):
	return calculate_amount_of_accounts_of_advance(filters,'Des Industry', indent=2)

def tg_steels(filters):
	return calculate_amount_of_accounts_of_debit(filters, 'TG Steel', '11601' , indent=2)

def customer_advances(filters):
	return calculate_amount_of_accounts_of_debit(filters, 'Customer Advances', '11200-01' ,indent=2)	

def deposits(filters):
	return {'Account': 'Deposits', 'Amount': '', 'indent': 2}

def contribution_to_tg_steel(filters):
	return calculate_amount_of_accounts_of_debit(filters, 'Contribution to TG steel', '11601' , indent=2)

def assets_total(asset_total):
	return {'Account': 'Asset Total', 'Amount': asset_total, 'indent': 1}

def liabilities(filters):
	return {'Account': 'Liabilities :', 'Amount': '', 'indent': 0}

def bank_loans(filters):
	return {'Account': 'Bank Loan', 'Amount': '', 'indent': 1}

def enat_bank_mercentile_loan(filters):
	return calculate_amount_of_accounts_of_creadit(filters, 'ENAT Bank - Mercentile Loan', '21200-02', indent=2)

def enat_bank_od_acc(filters):
	return calculate_amount_of_accounts_of_creadit(filters, 'ENAT Bank - OD A/c', '11120-19', indent=2)

def enat_bank_term_loan_acc(filters):
	return calculate_amount_of_accounts_of_creadit(filters, 'ENAT Bank - Term Loan A/c', '22100-01', indent=2)

def tax_liability_due():
	return {'Account': 'Tax liability due', 'Amount': '', 'indent': 1}

def vat_account(filters):
	return calculate_amount_of_accounts_of_creadit(filters, 'VAT', '21100-08',  indent=2)

def wht_account(filters):
	return calculate_amount_of_accounts_of_creadit(filters,'WHT', '21100-07', indent=2)

def penison_account(filters):
	return calculate_amount_of_accounts_of_creadit(filters, 'PENSION', '21100-02', indent=2)

def income_tax(filters):
	return calculate_amount_of_accounts_of_creadit(filters, 'Income Tax', '21100-01', indent=2)
	
def profit_tax_upto(filters):
	return calculate_amount_of_accounts_of_creadit(filters, 'Profit tax', '21100-09' ,indent=2)

def dividend_distribution():
	return {'Account': 'Dividend Distribution Tax', 'Amount': '', 'indent': 2}

def creditors():
	return {'Account': 'Creditors', 'Amount': '', 'indent': 1}

def trade_creditors(filters):
	return calculate_amount_of_accounts_of_creadit(filters, 'Trade Creditors (For Raw Materials)', '21000-01', indent=2)

def other_creditors(filters):
	return calculate_amount_of_accounts_of_creadit(filters, 'Other Creditors', '21200-03', indent=2)

def for_salary(filters):
	return calculate_amount_of_accounts_of_creadit(filters, 'For Salary', '21400-01',  indent=2)

def for_it_consultant(filters):
	return calculate_amount_of_accounts_of_debit(filters, 'Accrued Expenses (other than Salary)', '21400-02'  ,indent=2)

def liabilities_total(liabilit_total):
	return {'Account': 'Liabilities Total', 'Amount': liabilit_total, 'indent': 1}

def networths_total(amount):
	return {'Account': 'Networth Total', 'Amount': amount, 'indent': 0}	

def calculate_amount_of_accounts_of_debit(filters, account, account_number ,indent):
	accounts = get_monthly_gl_debit(filters, account_number)
	accounts_sum = sum(accounts)
	return {'Account': account, 'Amount': accounts_sum, 'indent': indent}

def calculate_amount_of_accounts_of_creadit(filters, account, account_number ,indent):
	accounts = get_monthly_gl_credit(filters, account_number)
	accounts_sum = sum(accounts)
	return {'Account': account, 'Amount': accounts_sum, 'indent': indent}

def calculate_amount_of_accounts_of_advance(filters, account, indent):
	accounts = get_monthly_gl_debit_no_opening_with_advances(filters, account)
	accounts_sum = sum(accounts)
	return {'Account': account, 'Amount': accounts_sum, 'indent': indent}	

def get_monthly_gl_debit(filters, account):
	a = frappe.db.sql("""select MONTH(posting_date) as month, sum(debit) from `tabGL Entry` where account like "{0}%" and (posting_date between '{1}' AND '{2}') GROUP BY MONTH(posting_date) ORDER BY month;""".format(account, filters.from_date, filters.to_date), as_list=True)
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


	b = frappe.db.sql("""select MONTH(posting_date) as month, sum(credit) from `tabGL Entry` where account like "{0}%" and (posting_date between '{1}' AND '{2}') GROUP BY MONTH(posting_date) ORDER BY month;""".format(account, filters.from_date, filters.to_date), as_list=True)
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
	
	return res_a

def get_monthly_gl_credit(filters, account):
		a = frappe.db.sql("""select MONTH(posting_date) as month, sum(credit) from `tabGL Entry` where account like "{0}%" and (posting_date between '{1}' AND '{2}') GROUP BY MONTH(posting_date) ORDER BY month;""".format(account, filters.from_date, filters.to_date), as_list=True)
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

		b = frappe.db.sql("""select MONTH(posting_date) as month, sum(debit) from `tabGL Entry` where account like "{0}%" and (posting_date between '{1}' AND '{2}') GROUP BY MONTH(posting_date) ORDER BY month;""".format(account, filters.from_date, filters.to_date), as_list=True)
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
	
		return res_a

def get_monthly_gl_debit_no_opening_with_advances(filters, account):
	a = frappe.db.sql("""select MONTH(posting_date) as month, sum(debit) from `tabGL Entry` where party_type='Customer' and party like '{0}%' and (posting_date between '{1}' AND '{2}') GROUP BY MONTH(posting_date) ORDER BY month;""".format(account, filters.from_date, filters.to_date), as_list=True)
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


	b = frappe.db.sql("""select MONTH(posting_date) as month, sum(credit) from `tabGL Entry` where party_type='Customer' and party like '{0}%' and (posting_date between '{1}' AND '{2}') GROUP BY MONTH(posting_date) ORDER BY month;""".format(account, filters.from_date, filters.to_date), as_list=True)
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

	return res_a

def get_monthly_gl_debit_no_opening(filters, account):
	now = datetime.now()
	last_year = now.year - 1
	from_date = str(last_year) + '-'  + '01' + '-'  + '01'
	to_date = str(last_year) + '-'  + '12' + '-'  + '31'
	a = frappe.db.sql("""select MONTH(posting_date) as month, sum(debit) from `tabGL Entry` where account like "{0}%" and (posting_date between '{1}' AND '{2}') GROUP BY MONTH(posting_date) ORDER BY month;""".format(account, from_date, to_date), as_list=True)
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

	b = frappe.db.sql("""select MONTH(posting_date) as month, sum(credit) from `tabGL Entry` where account like "{0}%" and (posting_date between '{1}' AND '{2}') GROUP BY MONTH(posting_date) ORDER BY month;""".format(account, filters.from_date, filters.to_date), as_list=True)
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
	# print("opening and total added is =====> ", fin)

	fin_abs= []
	for i in fin:
		abs_val = abs(i)
		fin_abs.append(abs_val)

	return fin_abs

def get_data(filters):
	data_list = []
	asset_total = 0
	liabilit_total = 0

	asset = assets()
	data_list.append(asset)

	fixed_asset = fixed_assets_gross_block(filters)
	print(fixed_asset)
	asset_total += fixed_asset['Amount']
	data_list.append(fixed_asset)
	
	stock_value = stock_value_market_price(filters)
	asset_total += stock_value['Amount']
	data_list.append(stock_value)
	
	cash_bank = cash_and_bank_account(filters)
	asset_total += cash_bank['Amount']
	data_list.append(cash_bank)
	
	advance = advances(filters)
	data_list.append(advance)
	
	debtors = debtors_customer_advances(filters)
	asset_total += debtors['Amount']
	data_list.append(debtors)
	
	des_genrl = des_general(filters)
	asset_total += des_genrl['Amount']
	data_list.append(des_genrl)
	
	des_indus = des_industries(filters)
	asset_total += des_indus['Amount']
	data_list.append(des_indus)
	
	tg_steel = tg_steels(filters)
	tg_steel_closing = get_monthly_gl_debit_no_opening(filters, '11601')
	tg_steel_opening_closing = tg_steel['Amount'] - sum(tg_steel_closing)
	tg_steel_total = {'Account': 'TG Steel', 'Amount': tg_steel_opening_closing, 'indent': 2}
	asset_total += tg_steel_opening_closing
	data_list.append(tg_steel_total)
	
	customer_advnce = customer_advances(filters)
	
	total = customer_advnce['Amount'] - des_genrl['Amount'] - des_indus['Amount']
	customer_advnce_total = {'Account': 'Customer Advances', 'Amount': total, 'indent': 2}
	asset_total += total
	data_list.append(customer_advnce_total)
	print(asset_total)
	deposit = deposits(filters)
	data_list.append(deposit)

	contribution_tg = contribution_to_tg_steel(filters)
	asset_total += contribution_tg['Amount']
	data_list.append(contribution_tg)
	
	asset_total_return = assets_total(asset_total)
	
	data_list.append(asset_total_return)

	liability = liabilities(filters)
	data_list.append(liability)

	bank_loan = bank_loans(filters)
	data_list.append(bank_loan)

	enat_bank_mercnt = enat_bank_mercentile_loan(filters)
	liabilit_total+= enat_bank_mercnt['Amount']
	data_list.append(enat_bank_mercnt)

	enat_bank_od = enat_bank_od_acc(filters)
	liabilit_total+= enat_bank_od['Amount']
	data_list.append(enat_bank_od)

	enat_bank_loan = enat_bank_term_loan_acc(filters)
	liabilit_total+= enat_bank_loan['Amount']
	data_list.append(enat_bank_loan)

	tax_due = tax_liability_due()
	data_list.append(tax_due)

	vat = vat_account(filters)
	liabilit_total+= vat['Amount']
	data_list.append(vat)

	wht = wht_account(filters)
	liabilit_total+= wht['Amount']
	data_list.append(wht)

	pension = penison_account(filters)
	liabilit_total+= pension['Amount']
	data_list.append(pension)

	income = income_tax(filters)
	liabilit_total+= income['Amount']
	data_list.append(income)

	profit_tax = profit_tax_upto(filters)
	liabilit_total+= profit_tax['Amount']
	data_list.append(profit_tax)

	divinded = dividend_distribution()
	# liabilit_total+= divinded['Amount']
	data_list.append(divinded)

	creditor = creditors()
	data_list.append(creditor)

	trade = trade_creditors(filters)
	liabilit_total+= trade['Amount']
	data_list.append(trade)

	other = other_creditors(filters)
	liabilit_total+= other['Amount']
	data_list.append(other)

	salary = for_salary(filters)
	liabilit_total+= salary['Amount']
	data_list.append(salary)

	it_consultant = for_it_consultant(filters)
	liabilit_total+= it_consultant['Amount']
	data_list.append(it_consultant)

	liability_total = liabilities_total(liabilit_total)
	data_list.append(liability_total)
	
	networth_total = asset_total - liabilit_total

	networth_total = networths_total(networth_total)
	data_list.append(networth_total)

	return data_list