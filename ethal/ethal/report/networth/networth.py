# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import pprint 

def execute(filters=None):
	columns, data = [], []
	data = get_data()
	columns = ["Account::280"]+["Amount::300"]
	return columns, data

def assets():
	return {'Account': 'Assets:', 'Amount': '', 'indent': 0}

def fixed_assets_gross_block():
	return calculate_amount_of_accounts_of_debit('Fixed Assets - Gross Block', '121', indent=1)

def stock_value_market_price():
	return calculate_amount_of_accounts_of_debit('Stock value ( Market price)', '115',indent=1,)

def cash_and_bank_account():
	return calculate_amount_of_accounts_of_debit('Cash &  Bank', '111', indent=1)

def advances():
	return {'Account': 'Advances', 'Amount': '', 'indent': 1}

def debtors_customer_advances():
	return calculate_amount_of_accounts_of_debit('(Debtors + Customer Advances)', '112', indent=2)
	
def des_general():
	return calculate_amount_of_accounts_of_advance('Des General ', indent=2)

def des_industries():
	return calculate_amount_of_accounts_of_advance('Des Industry', indent=2)

def tg_steels():
	return calculate_amount_of_accounts_of_debit('TG Steel', '11601' , indent=2)

def customer_advances():
	return calculate_amount_of_accounts_of_debit('Customer Advances', '11200-01' ,indent=2)	

def deposits():
	return {'Account': 'Deposits', 'Amount': '', 'indent': 2}

def contribution_to_tg_steel():
	return calculate_amount_of_accounts_of_debit('Contribution to TG steel', '11601' , indent=2)

def assets_total(asset_total):
	return {'Account': 'Asset Total', 'Amount': asset_total, 'indent': 1}

def liabilities():
	return {'Account': 'Liabilities :', 'Amount': '', 'indent': 0}

def bank_loans():
	return {'Account': 'Bank Loan', 'Amount': '', 'indent': 1}

def enat_bank_mercentile_loan():
	return calculate_amount_of_accounts_of_creadit('ENAT Bank - Mercentile Loan', '21200-02', indent=2)

def enat_bank_od_acc():
	return calculate_amount_of_accounts_of_creadit('ENAT Bank - OD A/c', '11120-19', indent=2)

def enat_bank_term_loan_acc():
	return calculate_amount_of_accounts_of_creadit('ENAT Bank - Term Loan A/c', '22100-01', indent=2)

def supplier_credit_payment_due_heading():
	return {'Account': 'Supplier Credit Payment Due', 'Amount': '', 'indent': 1}

def singhi_treading_co_ltd():
	return {'Account': 'Singhi Trading Co. Ltd', 'Amount': '', 'indent': 2}

def for_raw_materials():
	return {'Account': '(For Raw Materials - USD 657000)@ ETB 32.8128', 'Amount': '', 'indent': 2}

def for_fixed_assets_usd():
	return {'Account': '(For Fixed Assets - USD 392310)@ ETB 32.8128', 'Amount': '', 'indent': 2}

def tax_liability_due():
	return {'Account': 'Tax liability due', 'Amount': '', 'indent': 1}

def vat_account():
	return calculate_amount_of_accounts_of_creadit('VAT', '21100-08',  indent=2)

def wht_account():
	return calculate_amount_of_accounts_of_creadit('WHT', '21100-07', indent=2)

def penison_account():
	return calculate_amount_of_accounts_of_creadit('PENSION', '21100-02', indent=2)

def income_tax():
	return calculate_amount_of_accounts_of_creadit('Income Tax', '21100-01', indent=2)
	
def profit_tax_upto():
	return calculate_amount_of_accounts_of_creadit('Profit tax upto 31/12/2019', '21100-09' ,indent=2)

def dividend_distribution():
	return {'Account': 'Dividend Distribution Tax', 'Amount': '', 'indent': 2}

def creditors():
	return {'Account': 'Creditors', 'Amount': '', 'indent': 1}

def trade_creditors():
	return calculate_amount_of_accounts_of_creadit('Trade Creditors (For Raw Materials)', '21000-01', indent=2)

def other_creditors():
	return calculate_amount_of_accounts_of_creadit('Other Creditors', '21200-03', indent=2)

def for_salary():
	return calculate_amount_of_accounts_of_creadit('For Salary', '21400-01',  indent=2)

def for_it_consultant():
	return calculate_amount_of_accounts_of_debit('For IT consultant (Mulatu meknon)', '63000-01'  ,indent=2)

def for_security_services():
	return calculate_amount_of_accounts_of_debit('For Security Sevices', '54100-08', indent=2)

def for_bus_rental():
	return calculate_amount_of_accounts_of_debit('For Bus Rental', '54100-07',indent=2)

def for_telephone_and_internet_exp():
	return calculate_amount_of_accounts_of_debit('For Telephone & Internet Exp.', '63000-15',indent=2)

def for_water_bill():
	return calculate_amount_of_accounts_of_debit('For Water Bill', '54400-02', indent=2)

def for_electricity_charges():
	return calculate_amount_of_accounts_of_debit('For Electricity Charges', '54400-01', indent=2)

def for_solomon_bekele():
	return calculate_amount_of_accounts_of_debit('For Soloman Bekele (Labour Contractor)', '51000-02',indent=2)

def for_canteen_exp():
	return calculate_amount_of_accounts_of_debit('For Canteen Exp.', '54100-03', indent=2)

def for_account_consultancy():
	return {'Account': 'For Account Consultancy (GT)', 'Amount': '', 'indent': 2}

def solomon_consultant():
	return calculate_amount_of_accounts_of_debit('For Soloman (Consultant)', '63000-01', indent=2)

def michel_civil_work():
	return {'Account': 'For Michel (Civil Work)', 'Amount': '', 'indent': 2}

def liabilities_total(liabilit_total):
	return {'Account': 'Liabilities Total', 'Amount': liabilit_total, 'indent': 1}

def networths_total(amount):
	return {'Account': 'Networth Total', 'Amount': amount, 'indent': 0}	

def calculate_amount_of_accounts_of_debit(account, account_number ,indent):
	accounts = get_monthly_gl_debit(account_number)
	accounts_sum = sum(accounts)
	return {'Account': account, 'Amount': accounts_sum, 'indent': indent}

def calculate_amount_of_accounts_of_creadit(account, account_number ,indent):
	accounts = get_monthly_gl_credit(account_number)
	accounts_sum = sum(accounts)
	return {'Account': account, 'Amount': accounts_sum, 'indent': indent}

def calculate_amount_of_accounts_of_advance(account, indent):
	accounts = get_monthly_gl_debit_no_opening_with_advances(account)
	accounts_sum = sum(accounts)
	return {'Account': account, 'Amount': accounts_sum, 'indent': indent}	

def get_monthly_gl_debit(account):
	a = frappe.db.sql("""select MONTH(posting_date) as month, sum(debit) from `tabGL Entry` where account like "{0}%" and YEAR(posting_date) = 2020 GROUP BY MONTH(posting_date) ORDER BY month;""".format(account), as_list=True)
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


	b = frappe.db.sql("""select MONTH(posting_date) as month, sum(credit) from `tabGL Entry` where account like "{0}%" and YEAR(posting_date) = 2020 GROUP BY MONTH(posting_date) ORDER BY month;""".format(account), as_list=True)
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
	print(res_a)
	
	return res_a

def get_monthly_gl_credit(account):
		a = frappe.db.sql("""select MONTH(posting_date) as month, sum(credit) from `tabGL Entry` where account like "{0}%" and YEAR(posting_date) = 2020 GROUP BY MONTH(posting_date) ORDER BY month;""".format(account), as_list=True)
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

		b = frappe.db.sql("""select MONTH(posting_date) as month, sum(debit) from `tabGL Entry` where account like "{0}%" and YEAR(posting_date) = 2020 GROUP BY MONTH(posting_date) ORDER BY month;""".format(account), as_list=True)
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

def get_monthly_gl_debit_no_opening_with_advances(account):
	a = frappe.db.sql("""select MONTH(posting_date) as month, sum(debit) from `tabGL Entry` where party_type='Customer' and party like '{0}%'  and YEAR(posting_date) = 2020 GROUP BY MONTH(posting_date) ORDER BY month;""".format(account), as_list=True)
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


	b = frappe.db.sql("""select MONTH(posting_date) as month, sum(credit) from `tabGL Entry` where party_type='Customer' and party like '{0}%'  and YEAR(posting_date) = 2020 GROUP BY MONTH(posting_date) ORDER BY month;""".format(account), as_list=True)
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

def get_monthly_gl_debit_no_opening(account):
	a = frappe.db.sql("""select MONTH(posting_date) as month, sum(debit) from `tabGL Entry` where account like "{0}%" and YEAR(posting_date) = 2019 GROUP BY MONTH(posting_date) ORDER BY month;""".format(account), as_list=True)
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

	b = frappe.db.sql("""select MONTH(posting_date) as month, sum(credit) from `tabGL Entry` where account like "{0}%" and YEAR(posting_date) = 2020 GROUP BY MONTH(posting_date) ORDER BY month;""".format(account), as_list=True)
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

def get_data():
	data_list = []
	asset_total = 0
	liabilit_total = 0

	asset = assets()
	data_list.append(asset)

	fixed_asset = fixed_assets_gross_block()
	asset_total += fixed_asset['Amount']
	data_list.append(fixed_asset)

	stock_value = stock_value_market_price()
	asset_total += stock_value['Amount']
	data_list.append(stock_value)

	cash_bank = cash_and_bank_account()
	asset_total += cash_bank['Amount']
	data_list.append(cash_bank)

	advance = advances()
	data_list.append(advance)

	debtors = debtors_customer_advances()
	asset_total += debtors['Amount']
	data_list.append(debtors)

	des_genrl = des_general()
	asset_total += des_genrl['Amount']
	data_list.append(des_genrl)

	des_indus = des_industries()
	asset_total += des_indus['Amount']
	data_list.append(des_indus)

	tg_steel = tg_steels()
	tg_steel_closing = get_monthly_gl_debit_no_opening('11601')
	tg_steel_opening_closing = tg_steel['Amount'] - sum(tg_steel_closing)
	tg_steel_total = {'Account': 'TG Steel', 'Amount': tg_steel_opening_closing, 'indent': 2}
	asset_total += tg_steel_opening_closing
	data_list.append(tg_steel_total)

	customer_advnce = customer_advances()
	asset_total += customer_advnce['Amount']
	total = customer_advnce['Amount'] - des_genrl['Amount'] - des_indus['Amount']
	customer_advnce_total = {'Account': 'Customer Advances', 'Amount': total, 'indent': 2}
	data_list.append(customer_advnce_total)

	deposit = deposits()
	data_list.append(deposit)

	contribution_tg = contribution_to_tg_steel()
	asset_total += contribution_tg['Amount']
	data_list.append(contribution_tg)

	asset_total_return = assets_total(asset_total)
	data_list.append(asset_total_return)

	liability = liabilities()
	data_list.append(liability)

	bank_loan = bank_loans()
	data_list.append(bank_loan)

	enat_bank_mercnt = enat_bank_mercentile_loan()
	liabilit_total+= enat_bank_mercnt['Amount']
	data_list.append(enat_bank_mercnt)

	enat_bank_od = enat_bank_od_acc()
	liabilit_total+= enat_bank_od['Amount']
	data_list.append(enat_bank_od)

	enat_bank_loan = enat_bank_term_loan_acc()
	liabilit_total+= enat_bank_loan['Amount']
	data_list.append(enat_bank_loan)

	supplier_credit = supplier_credit_payment_due_heading()
	data_list.append(supplier_credit)

	singhi_treding = singhi_treading_co_ltd()
	# liabilit_total+= singhi_treding['Amount']
	data_list.append(singhi_treding)

	for_material = for_raw_materials()
	# liabilit_total+= for_material['Amount']
	data_list.append(for_material)

	for_fixed = for_fixed_assets_usd()
	# liabilit_total+= for_fixed['Amount']
	data_list.append(for_fixed)

	tax_due = tax_liability_due()
	data_list.append(tax_due)

	vat = vat_account()
	liabilit_total+= vat['Amount']
	data_list.append(vat)

	wht = wht_account()
	liabilit_total+= wht['Amount']
	data_list.append(wht)

	pension = penison_account()
	liabilit_total+= pension['Amount']
	data_list.append(pension)

	income = income_tax()
	liabilit_total+= income['Amount']
	data_list.append(income)

	profit_tax = profit_tax_upto()
	liabilit_total+= profit_tax['Amount']
	data_list.append(profit_tax)

	divinded = dividend_distribution()
	# liabilit_total+= divinded['Amount']
	data_list.append(divinded)

	creditor = creditors()
	data_list.append(creditor)

	trade = trade_creditors()
	liabilit_total+= trade['Amount']
	data_list.append(trade)

	other = other_creditors()
	liabilit_total+= other['Amount']
	data_list.append(other)

	salary = for_salary()
	liabilit_total+= salary['Amount']
	data_list.append(salary)

	it_consultant = for_it_consultant()
	liabilit_total+= it_consultant['Amount']
	data_list.append(it_consultant)

	security = for_security_services()
	liabilit_total+= security['Amount']
	data_list.append(security)

	bus_rental = for_bus_rental()
	liabilit_total+= bus_rental['Amount']
	data_list.append(bus_rental)

	telephone = for_telephone_and_internet_exp()
	liabilit_total+= telephone['Amount']
	data_list.append(telephone)

	water = for_water_bill()
	liabilit_total+= water['Amount']
	data_list.append(water)

	electricity = for_electricity_charges()
	liabilit_total+= electricity['Amount']
	data_list.append(electricity)

	solomon_bekele = for_solomon_bekele()
	liabilit_total+= solomon_bekele['Amount']
	data_list.append(solomon_bekele)

	canteen = for_canteen_exp()
	liabilit_total+= canteen['Amount']
	data_list.append(canteen)

	account_consultncy = for_account_consultancy()
	# liabilit_total+= account_consultncy['Amount']
	data_list.append(account_consultncy)

	solomon_consul = solomon_consultant()
	liabilit_total+= solomon_consul['Amount']
	data_list.append(solomon_consul)

	michel = michel_civil_work()
	# liabilit_total+= michel['Amount']
	data_list.append(michel)

	liability_total = liabilities_total(liabilit_total)
	data_list.append(liability_total)
	
	networth_total = asset_total - liabilit_total

	networth_total = networths_total(networth_total)
	data_list.append(networth_total)

	return data_list