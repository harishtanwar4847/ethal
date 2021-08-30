# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import datetime
import calendar
import frappe, erpnext
from erpnext import get_company_currency, get_default_company
from erpnext.accounts.report.utils import get_currency, convert_to_presentation_currency
from frappe.utils import getdate, cstr, flt, fmt_money
from frappe import _, _dict
from erpnext.accounts.utils import get_account_currency
from erpnext.accounts.report.financial_statements import get_cost_centers_with_children
from erpnext.accounts.report.general_ledger.general_ledger import validate_filters, validate_party, set_account_currency, get_result, get_gl_entries, get_conditions, get_data_with_opening_closing, get_totals_dict, group_by_field, initialize_gle_map, get_accountwise_gle, get_result_as_list, get_supplier_invoice_details, get_balance
from six import iteritems
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import get_accounting_dimensions, get_dimension_with_children
from collections import OrderedDict

def execute(filters=None):
	year = int(frappe.defaults.get_user_default("fiscal_year"))

	if not filters:
		return [], []

	account_details = {}

	if filters and filters.get('print_in_account_currency') and \
		not filters.get('account'):
		frappe.throw(_("Select an account to print in account currency"))

	for acc in frappe.db.sql("""select name, is_group from tabAccount""", as_dict=1):
		account_details.setdefault(acc.name, acc)

	if filters.get('party'):
		filters.party = frappe.parse_json(filters.get("party"))

	validate_filters(filters, account_details)

	validate_party(filters)

	filters = set_account_currency(filters)

	columns = ["Month::180"]+["Gross Profit Margin::180"]+["Net Profit Margin::180"]+["EBITDA Margin::180"]+["EBIT Margin::180"]+["Return on Assets::180"]+["Return on Equity::180"]
	# res_data_41000_total = result_data_total("41000 - Direct Income - ETL",filters, account_details)
	res_data_41000_total = []
	for i in range(1,13):
		date = datetime.datetime(year,i,15).strftime("%Y-%m-%d")
		first_date = frappe.db.sql("""select DATE_ADD(DATE_ADD(LAST_DAY('{0}'), INTERVAL 1 DAY), INTERVAL - 1 MONTH)""".format(date))
		for i in first_date:
			for j in i:
				first_date = j
		last_date = frappe.db.sql("""SELECT LAST_DAY("{0}");""".format(date))
		for i in last_date:
			for j in i:
				last_date = j
		filters['presentation_currency'] = 'Ethiopia Birrr'
		filters['account_currency'] = 'Ethiopia Birrr'
		filters["from_date"] = first_date
		filters["to_date"] = last_date
		filters["account"] = "41000 - Direct Income - E21"
		res = get_result(filters, account_details)
		res_data_41000_total.append(res[-2]["balance"])


	# res_data_50000_total = result_data_total("50000 - Direct Costs - ETL",filters, account_details)
	res_data_50000_total = []
	for i in range(1,13):
		date = datetime.datetime(year,i,15).strftime("%Y-%m-%d")
		first_date = frappe.db.sql("""select DATE_ADD(DATE_ADD(LAST_DAY('{0}'), INTERVAL 1 DAY), INTERVAL - 1 MONTH)""".format(date))
		for i in first_date:
			for j in i:
				first_date = j
		last_date = frappe.db.sql("""SELECT LAST_DAY("{0}");""".format(date))
		for i in last_date:
			for j in i:
				last_date = j
		filters['presentation_currency'] = 'Ethiopia Birrr'
		filters['account_currency'] = 'Ethiopia Birrr'
		filters["from_date"] = first_date
		filters["to_date"] = last_date
		filters["account"] = "50000 - Direct Costs - E21"
		res = get_result(filters, account_details)
		res_data_50000_total.append(res[-2]["balance"])

	# res_data_40000_total = result_data_total("40000 - Income - ETL",filters, account_details)
	res_data_40000_total = []
	for i in range(1,13):
		date = datetime.datetime(year,i,15).strftime("%Y-%m-%d")
		first_date = frappe.db.sql("""select DATE_ADD(DATE_ADD(LAST_DAY('{0}'), INTERVAL 1 DAY), INTERVAL - 1 MONTH)""".format(date))
		for i in first_date:
			for j in i:
				first_date = j
		last_date = frappe.db.sql("""SELECT LAST_DAY("{0}");""".format(date))
		for i in last_date:
			for j in i:
				last_date = j
		filters['presentation_currency'] = 'Ethiopia Birrr'
		filters['account_currency'] = 'Ethiopia Birrr'
		filters["from_date"] = first_date
		filters["to_date"] = last_date
		filters["account"] = "40000 - Income - E21"
		res = get_result(filters, account_details)
		res_data_40000_total.append(res[-2]["balance"])

	# res_data_60000_total = result_data_total("60000 - Indirect Costs - ETL",filters, account_details)
	res_data_60000_total = []
	for i in range(1,13):
		date = datetime.datetime(year,i,15).strftime("%Y-%m-%d")
		first_date = frappe.db.sql("""select DATE_ADD(DATE_ADD(LAST_DAY('{0}'), INTERVAL 1 DAY), INTERVAL - 1 MONTH)""".format(date))
		for i in first_date:
			for j in i:
				first_date = j
		last_date = frappe.db.sql("""SELECT LAST_DAY("{0}");""".format(date))
		for i in last_date:
			for j in i:
				last_date = j
		filters["from_date"] = first_date
		filters["to_date"] = last_date
		filters["account"] = "60000 - General and Administrative Expenses - E21"
		res = get_result(filters, account_details)
		res_data_60000_total.append(res[-2]["balance"])

	# res_data_62000_total = result_data_total("62000 - Financial expenses - ETL",filters, account_details)
	res_data_62000_total = []
	for i in range(1,13):
		date = datetime.datetime(year,i,15).strftime("%Y-%m-%d")
		first_date = frappe.db.sql("""select DATE_ADD(DATE_ADD(LAST_DAY('{0}'), INTERVAL 1 DAY), INTERVAL - 1 MONTH)""".format(date))
		for i in first_date:
			for j in i:
				first_date = j
		last_date = frappe.db.sql("""SELECT LAST_DAY("{0}");""".format(date))
		for i in last_date:
			for j in i:
				last_date = j
		filters["from_date"] = first_date
		filters["to_date"] = last_date
		filters["account"] = "62000 - Tax Expense - E21"
		res = get_result(filters, account_details)
		res_data_62000_total.append(res[-2]["balance"])

	# res_data_63000_16_total = result_data_total("63000-16 - Depreciation - ETL",filters, account_details)
	# res_data_63000_16_total = []
	# for i in range(1,13):
	# 	date = datetime.datetime(year,i,15).strftime("%Y-%m-%d")
	# 	first_date = frappe.db.sql("""select DATE_ADD(DATE_ADD(LAST_DAY('{0}'), INTERVAL 1 DAY), INTERVAL - 1 MONTH)""".format(date))
	# 	for i in first_date:
	# 		for j in i:
	# 			first_date = j
	# 	last_date = frappe.db.sql("""SELECT LAST_DAY("{0}");""".format(date))
	# 	for i in last_date:
	# 		for j in i:
	# 			last_date = j
	# 	filters["from_date"] = first_date
	# 	filters["to_date"] = last_date
	# 	filters["account"] = "63000-16 - Depreciation - ETL"
	# 	res = get_result(filters, account_details)
	# 	res_data_63000_16_total.append(res[-2]["balance"])


	# res_data_10000_closing = result_data_closing("10000 - Application of Funds (Assets) - ETL",filters, account_details)
	res_data_10000_closing = []
	for i in range(1,13):
		date = datetime.datetime(year,i,15).strftime("%Y-%m-%d")
		first_date = frappe.db.sql("""select DATE_ADD(DATE_ADD(LAST_DAY('{0}'), INTERVAL 1 DAY), INTERVAL - 1 MONTH)""".format(date))
		for i in first_date:
			for j in i:
				first_date = j
		last_date = frappe.db.sql("""SELECT LAST_DAY("{0}");""".format(date))
		for i in last_date:
			for j in i:
				last_date = j
		filters["from_date"] = first_date
		filters["to_date"] = last_date
		filters["account"] = "10000 - Application of Funds - E21"
		res = get_result(filters, account_details)
		res_data_10000_closing.append(res[-1]["balance"])


	# res_data_30000_closing = result_data_closing("30000 - Capital - ETL",filters, account_details)
	res_data_30000_closing = []
	for i in range(1,13):
		date = datetime.datetime(year,i,15).strftime("%Y-%m-%d")
		first_date = frappe.db.sql("""select DATE_ADD(DATE_ADD(LAST_DAY('{0}'), INTERVAL 1 DAY), INTERVAL - 1 MONTH)""".format(date))
		for i in first_date:
			for j in i:
				first_date = j
		last_date = frappe.db.sql("""SELECT LAST_DAY("{0}");""".format(date))
		for i in last_date:
			for j in i:
				last_date = j
		filters["from_date"] = first_date
		filters["to_date"] = last_date
		filters["account"] = "30000 - Capital - E21"
		res = get_result(filters, account_details)
		res_data_30000_closing.append(res[-1]["balance"])

	# res_data_50000_closing = result_data_closing("50000 - Direct Costs - ETL",filters, account_details)
	res_data_50000_closing = []
	for i in range(1,13):
		date = datetime.datetime(year,i,15).strftime("%Y-%m-%d")
		first_date = frappe.db.sql("""select DATE_ADD(DATE_ADD(LAST_DAY('{0}'), INTERVAL 1 DAY), INTERVAL - 1 MONTH)""".format(date))
		for i in first_date:
			for j in i:
				first_date = j
		last_date = frappe.db.sql("""SELECT LAST_DAY("{0}");""".format(date))
		for i in last_date:
			for j in i:
				last_date = j
		filters["from_date"] = first_date
		filters["to_date"] = last_date
		filters["account"] = "50000 - Direct Costs - E21"
		res = get_result(filters, account_details)
		res_data_50000_closing.append(res[-1]["balance"])

	# res_data_40000_closing = result_data_closing("40000 - Income - ETL",filters, account_details)
	res_data_40000_closing = []
	for i in range(1,13):
		date = datetime.datetime(year,i,15).strftime("%Y-%m-%d")
		first_date = frappe.db.sql("""select DATE_ADD(DATE_ADD(LAST_DAY('{0}'), INTERVAL 1 DAY), INTERVAL - 1 MONTH)""".format(date))
		for i in first_date:
			for j in i:
				first_date = j
		last_date = frappe.db.sql("""SELECT LAST_DAY("{0}");""".format(date))
		for i in last_date:
			for j in i:
				last_date = j
		filters["from_date"] = first_date
		filters["to_date"] = last_date
		filters["account"] = "40000 - Income - E21"
		res = get_result(filters, account_details)
		res_data_40000_closing.append(res[-1]["balance"])

	# res_data_60000_closing = result_data_closing("60000 - Indirect Costs - ETL",filters, account_details)
	res_data_60000_closing = []
	for i in range(1,13):
		date = datetime.datetime(year,i,15).strftime("%Y-%m-%d")
		first_date = frappe.db.sql("""select DATE_ADD(DATE_ADD(LAST_DAY('{0}'), INTERVAL 1 DAY), INTERVAL - 1 MONTH)""".format(date))
		for i in first_date:
			for j in i:
				first_date = j
		last_date = frappe.db.sql("""SELECT LAST_DAY("{0}");""".format(date))
		for i in last_date:
			for j in i:
				last_date = j
		filters["from_date"] = first_date
		filters["to_date"] = last_date
		filters["account"] = "60000 - General and Administrative Expenses - E21"
		res = get_result(filters, account_details)
		res_data_60000_closing.append(res[-1]["balance"])


	gpm_numerator = [b - m  for b,m in zip(res_data_41000_total, res_data_50000_total)]
	gross_profit_margin = [(b / m)*100 if m != 0 and b!=0 else 0 for b,m in zip(gpm_numerator, res_data_41000_total)]
	gross_profit_margin = absolute_value(gross_profit_margin)


	npm_numerator = [b - m - c  for b,m,c in zip(res_data_40000_total, res_data_50000_total,res_data_60000_total)]
	net_profit_margin = [(b / m)*100 if m != 0 and b!=0 else 0 for b,m in zip(npm_numerator, res_data_40000_total)]
	net_profit_margin= absolute_value(net_profit_margin)

	ebidta_margin_numerator = [a-b-c+d for a,b,c,d in zip(res_data_40000_total,res_data_50000_total,res_data_60000_total,res_data_62000_total)]
	ebidta_margin = [(b / m)*100 if m != 0 and b!=0 else 0 for b,m in zip(ebidta_margin_numerator, res_data_41000_total)]
	ebidta_margin = absolute_value(ebidta_margin)

	ebit_margin_numerator = [a-b-c+d  for a,b,c,d in zip(res_data_40000_total,res_data_50000_total,res_data_60000_total,res_data_62000_total)]
	ebit_margin = [(b / m)*100 if m != 0 and b!=0 else 0 for b,m in zip(ebit_margin_numerator, res_data_41000_total)]
	ebit_margin = absolute_value(ebit_margin)

	roa_numerator = [a-b-c for a,b,c in zip(res_data_40000_total,res_data_50000_total,res_data_60000_total)]
	roa = [(b / m)*100 if m != 0 and b!=0 else 0 for b,m in zip(roa_numerator, res_data_10000_closing)]
	roa = absolute_value(roa)

	roe_numerator = [a-b-c for a,b,c in zip(res_data_40000_total,res_data_50000_total,res_data_60000_total)]
	roe_denominator = [a+(b-c-e) for a,b,c,e in zip(res_data_30000_closing,res_data_40000_closing,res_data_50000_closing,res_data_60000_closing)]
	roe = [(b / m)*100 if m != 0 and b!=0 else 0 for b,m in zip(roe_numerator, roe_denominator)]
	roe = absolute_value(roe)

	month = ["Jan","Feb","Mar","April","May","June","July","Aug","Sept","Oct","Nov","Dec"]
	rep= []
	for (a,b,c,d,e,f,g) in zip(month,gross_profit_margin,net_profit_margin,ebidta_margin,ebit_margin,roa,roe):
		rep.append([a,b,c,d,e,f,g])

	return columns, rep



def absolute_value(val):
	fin_abs= []
	for i in val:
		abs_val = abs(i)
		fin_abs.append(abs_val)

	return fin_abs

# def result_data_total(account_name,filters, account_details):
# 	year = int(frappe.defaults.get_user_default("fiscal_year"))
# 	res_data = []

# 	for i in range(1,13):
# 		date = datetime.datetime(year,i,15).strftime("%Y-%m-%d")
# 		first_date = frappe.db.sql("""select DATE_ADD(DATE_ADD(LAST_DAY('{0}'), INTERVAL 1 DAY), INTERVAL - 1 MONTH)""".format(date))
# 		for i in first_date:
# 			for j in i:
# 				first_date = j
# 		last_date = frappe.db.sql("""SELECT LAST_DAY("{0}");""".format(date))
# 		for i in last_date:
# 			for j in i:
# 				last_date = j
# 		filters["from_date"] = first_date
# 		filters["to_date"] = last_date
# 		filters["account"] = account_name
# 		res = get_result(filters, account_details)
# 		res_data.append(res[-2]["balance"])

# 	return res_data

# def result_data_closing(account_name,filters, account_details):
# 	year = int(frappe.defaults.get_user_default("fiscal_year"))
# 	res_data = []

# 	for i in range(1,13):
# 		date = datetime.datetime(year,i,15).strftime("%Y-%m-%d")
# 		first_date = frappe.db.sql("""select DATE_ADD(DATE_ADD(LAST_DAY('{0}'), INTERVAL 1 DAY), INTERVAL - 1 MONTH)""".format(date))
# 		for i in first_date:
# 			for j in i:
# 				first_date = j
# 		last_date = frappe.db.sql("""SELECT LAST_DAY("{0}");""".format(date))
# 		for i in last_date:
# 			for j in i:
# 				last_date = j
# 		filters["from_date"] = first_date
# 		filters["to_date"] = last_date
# 		filters["account"] = account_name
# 		res = get_result(filters, account_details)
# 		res_data.append(res[-1]["balance"])

# 	return res_data