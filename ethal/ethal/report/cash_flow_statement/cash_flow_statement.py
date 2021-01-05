# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	columns = [
		{
			"label": "Account",
			"fieldname": "account",
			"fieldtype": "Data",
			"width": 250
		},
		{
			"label": "ETB",
			"fieldname": "etb",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "ETB",
			"fieldname": "etb1",
			"fieldtype": "Data",
			"width": 150
		}
	]
	data = get_data(filters)
	return columns, data

def cash_flows_operating_activities():
	return {'account': 'Cash flows from operating activities', 'etb': '', 'indent': 0}

def cash_receipt_from_customer(party_type, payment_type, from_date, to_date):
	a = get_payment_entry_value(party_type, payment_type, from_date, to_date)
	return {'account': 'Cash receipts from customers', 'etb': a, 'indent': 1}

def cash_paid_to_supplier(party_type, payment_type, from_date, to_date):
	a = get_payment_entry_value(party_type, payment_type, from_date, to_date)
	return {'account': 'Cash paid to suppliers', 'etb': "-"+str(a), 'indent': 1}

def cash_paid_to_employee(party_type, payment_type, from_date, to_date):
	a = get_payment_entry_value(party_type, payment_type, from_date, to_date)
	return {'account': 'Cash paid to employees', 'etb': "-"+str(a), 'indent': 1}

def cash_generated_from_operation(account_number, from_date, to_date):
	a = get_monthly_gl_credit(account_number, from_date, to_date)
	return {'account': 'Cash generated from operations', 'etb': a, 'indent': 1}

def interest_paid(account_number, from_date, to_date):
	a = get_monthly_gl_debit_for_negative(account_number, from_date, to_date)
	return {'account': 'Interest paid', 'etb': a, 'indent': 1}

def income_tax_paid(account_number, from_date, to_date):
	a = get_monthly_debit_gl_credit(account_number, from_date, to_date)	
	return {'account': 'Income taxes paid', 'etb': a, 'indent': 1}

def net_cash_from_operating_activities(total_flows):
	return {'account': 'Net cash from operating activities', 'etb1': total_flows, 'indent': 1}

def cash_flows_investing_activities():
	return {'account': 'Cash flows from investing activities', 'etb': '', 'indent': 0}

def get_payment_entry_value(party_type, payment_type, from_date, to_date):
	return frappe.db.sql(""" 
	select sum(paid_amount) from `tabPayment Entry` where party_type = '{}' and payment_type='{}' and (posting_date between '{}' and '{}')
	""".format(party_type, payment_type, from_date, to_date), as_list=1)[0][0]	

def purchase_of_property_plant_equipment(account_number, from_date, to_date):
	a = get_monthly_gl_debit_for_negative(account_number, from_date, to_date)
	return {'account': 'Purchase of property, plant, and equipment', 'etb': a, 'indent': 1}

def process_from_sales_equipment():
	return {'account': 'Proceeds from sale of equipment', 'etb': '', 'indent': 1}

def net_cash_used_in_investing_activities(total_cash_flows_investing):
	return { 'account': 'Net cash used in investing activities', 'etb1': total_cash_flows_investing, 'indent': 1}

def cash_flows_from_financing_activities():
	return {'account': 'Cash flows from financing activities', 'etb': '', 'indent': 0}

def proceed_from_issuance_common_stock(account_number, from_date, to_date):
	a = get_monthly_gl_debit(account_number, from_date, to_date)
	return {'account': 'Proceeds from issuance of common stock', 'etb': a, 'indent': 1}

def proceed_from_issuance_long_term_dept(account_number, from_date, to_date):
	a = get_monthly_gl_debit(account_number, from_date, to_date)
	return {'account': 'Proceeds from issuance of long-term debt', 'etb': a, 'indent': 1}

def principle_payment_under_capital(account_number, from_date, to_date):
	a = get_monthly_gl_debit_for_negative(account_number, from_date, to_date)
	return {'account': 'Principal payments under capital lease obligation', 'etb': a, 'indent': 1}

def dividends_paid():
	return {'account': 'Dividends paid', 'etb': '', 'indent': 1}

def net_cash_used_in_financing_activities(total_cash_flows_financing):
	return {'account': 'Net cash used in financing activities', 'etb1': total_cash_flows_financing, 'indent': 1}	

def net_increase(amount):
	return {'account': 'Net increase in cash and cash equivalents', 'etb1': amount, 'indent': 0}

def cash_and_cash_equivalents_at_beginning():
	return {'account': 'Cash and cash equivalents at beginning of period', 'etb1': '', 'indent': 0}

def cash_and_cash_equivalents_at_end(total):
	return {'account': 'Cash and cash equivalents at end of period', 'etb1': total, 'indent': 0}

def get_monthly_gl_credit(account, from_date, to_date):
	credit_amount_of_current_date = frappe.db.sql("""select sum(credit) from `tabGL Entry` where account like "{0}%" and (posting_date between '{1}' and '{2}') ;""".format(account, from_date, to_date), as_list=True)
	debit_amount_of_current_date = frappe.db.sql("""select sum(debit) from `tabGL Entry` where account like "{0}%" and (posting_date between '{1}' and '{2}');""".format(account, from_date, to_date), as_list=True)
	res_a = []
	
	if (credit_amount_of_current_date[0][0] != None and debit_amount_of_current_date[0][0] != None):  
		res_a = credit_amount_of_current_date[0][0] - debit_amount_of_current_date[0][0]
	
	credit_amount_of_previous_date = frappe.db.sql("""select sum(credit) from `tabGL Entry` where account like "{0}%" and (posting_date between '{1}' and '{2}') and month(posting_date) -1 ;""".format(account, from_date, to_date), as_list=True)
	debit_amount_of_previous_date = frappe.db.sql("""select sum(debit) from `tabGL Entry` where account like "{0}%" and (posting_date between '{1}' and '{2}') and month(posting_date) -1 ;""".format(account, from_date, to_date), as_list=True)
	res_b = []

	if (credit_amount_of_previous_date[0][0] != None and debit_amount_of_previous_date[0][0] != None):  
		res_b = credit_amount_of_previous_date[0][0] - debit_amount_of_previous_date[0][0]

	final_res = res_a+res_b
	
	return final_res

def get_monthly_gl_debit_for_negative(account, from_date, to_date):
	a = frappe.db.sql("""select sum(credit) from `tabGL Entry` where account like "{0}%" and (posting_date between '{1}' and '{2}') ;""".format(account, from_date, to_date), as_list=True)
	print(a)
	b = frappe.db.sql("""select sum(debit) from `tabGL Entry` where account like "{0}%" and (posting_date between '{1}' and '{2}') ;""".format(account, from_date, to_date), as_list=True)
	if (a[0][0] != None and b[0][0] != None):  
		res_a = a[0][0] - b[0][0]

		return res_a

def get_monthly_gl_debit(account, from_date, to_date):
	a = frappe.db.sql("""select sum(debit) from `tabGL Entry` where account like "{0}%" and (posting_date between '{1}' and '{2}') ;""".format(account, from_date, to_date), as_list=True)
	print(a)
	b = frappe.db.sql("""select sum(credit) from `tabGL Entry` where account like "{0}%" and (posting_date between '{1}' and '{2}') ;""".format(account, from_date, to_date), as_list=True)
	if (a[0][0] != None and b[0][0] != None):  
		res_a = a[0][0] - b[0][0]

		return res_a		

def get_monthly_debit_gl_credit(account, from_date, to_date):
	a = frappe.db.sql("""select sum(debit) from `tabGL Entry` where account like "{0}%" and (posting_date between '{1}' and '{2}') ;""".format(account, from_date, to_date), as_list=True)
	if a[0][0] != None:
		return a[0][0]

def get_data(filters):
	data_list = []
	total_flows = 0
	total_cash_flows_investing = 0
	total_cash_flows_financing = 0

	cfoa = cash_flows_operating_activities()
	data_list.append(cfoa)

	crfc = cash_receipt_from_customer('Customer', 'Receive', filters.from_date, filters.to_date)
	data_list.append(crfc)

	cpts = cash_paid_to_supplier('Supplier', 'Pay', filters.from_date, filters.to_date)
	data_list.append(cpts)

	cpte = cash_paid_to_employee('Employee', 'Pay', filters.from_date, filters.to_date)
	data_list.append(cpte)

	cgfo = cash_generated_from_operation('41', filters.from_date, filters.to_date)
	total_flows += cgfo['etb'] if cgfo['etb'] != None else 0
	data_list.append(cgfo)

	ip = interest_paid('62', filters.from_date, filters.to_date)
	total_flows += ip['etb'] if ip['etb'] != None else 0
	data_list.append(ip)

	itp = income_tax_paid('21100-01 ', filters.from_date, filters.to_date)
	total_flows += itp['etb'] if itp['etb'] != None else 0
	data_list.append(itp)

	ncfoa = net_cash_from_operating_activities(total_flows)
	data_list.append(ncfoa)

	cfia = cash_flows_investing_activities()
	data_list.append(cfia)

	pppe = purchase_of_property_plant_equipment('121', filters.from_date, filters.to_date)
	total_cash_flows_investing += pppe['etb'] if pppe['etb'] != None else 0
	data_list.append(pppe)

	pfse = process_from_sales_equipment()
	data_list.append(pfse)

	ncuia = net_cash_used_in_investing_activities(total_cash_flows_investing)
	data_list.append(ncuia)

	cfffa = cash_flows_from_financing_activities()
	data_list.append(cfffa)

	pfics = proceed_from_issuance_common_stock('63000-23', filters.from_date, filters.to_date)
	total_cash_flows_financing += pfics['etb'] if pfics['etb'] != None else 0
	data_list.append(pfics)

	pfild = proceed_from_issuance_long_term_dept('221', filters.from_date, filters.to_date)
	total_cash_flows_financing += pfild['etb'] if pfild['etb'] != None else 0
	data_list.append(pfild)

	ppuc = principle_payment_under_capital('22200', filters.from_date, filters.to_date)
	total_cash_flows_financing += ppuc['etb'] if ppuc['etb'] != None else 0
	data_list.append(ppuc)

	dp = dividends_paid()
	data_list.append(dp)

	ncufa = net_cash_used_in_financing_activities(total_cash_flows_financing)
	data_list.append(ncufa)

	total_flows_amount = total_flows+total_cash_flows_investing+total_cash_flows_financing
	ni = net_increase(total_flows_amount)
	data_list.append(ni)

	caceb = cash_and_cash_equivalents_at_beginning()
	data_list.append(caceb)

	cacee = cash_and_cash_equivalents_at_end(total_flows_amount)
	data_list.append(cacee)

	return data_list
