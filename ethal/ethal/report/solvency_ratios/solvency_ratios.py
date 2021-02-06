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
from six import iteritems
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import get_accounting_dimensions, get_dimension_with_children
from collections import OrderedDict
from erpnext.accounts.report.general_ledger.general_ledger import (validate_filters, validate_party, set_account_currency, get_result, get_gl_entries, 
get_conditions, get_data_with_opening_closing, get_accountwise_gle)

def execute(filters=None):

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

	columns = ["Month::180"]+["Debt to Assets::180"]+["Debt to Equity /Leverage (gearing) ratio::180"]+["Interest Coverage::180"]

	res_data_20000 = get_result_with_filters('20000 - Source of Funds (Liabilities) - ETL', filters, account_details)
	res_data_10000 = get_result_with_filters('10000 - Application of Funds (Assets) - ETL', filters, account_details)
	res_data_30000 = get_result_with_filters('30000 - Capital - ETL', filters, account_details)
	res_data_40000 = get_result_with_filters('40000 - Income - ETL', filters, account_details)
	res_data_50000 = get_result_with_filters('50000 - Direct Costs - ETL', filters, account_details)
	res_data_60000 = get_result_with_filters('60000 - Indirect Costs - ETL', filters, account_details)
	res_data_62000 = get_result_with_filters('62000 - Financial expenses - ETL', filters, account_details)

	debt_of_assets = [(b / m)*100 if m !=0 for b,m in zip(res_data_20000, res_data_10000)]
	debt_of_assets = aboslute_value(debt_of_assets)
	print("dets os assets =====================")
	print(debt_of_assets)
	debt_to_enquiry = [(a+(b-c-d)) for a,b,c,d in zip(res_data_30000, res_data_40000, res_data_50000, res_data_60000)]
	debt_to_enquiry_leverage = [(a/b)*100 if b !=0 for a,b in zip(res_data_20000, debt_to_enquiry)]
	debt_to_enquiry_leverage = aboslute_value(debt_to_enquiry_leverage)
	interest = [(a-b-c+d) for a,b,c,d in zip(res_data_40000, res_data_50000, res_data_60000, res_data_62000) ]
	interest_coverage = [(b/a)*100 if a !=0 for a,b in zip(interest, res_data_62000)]
	interest_coverage = aboslute_value(interest_coverage)
	print("=======dept of enquiry=============")
	print(debt_to_enquiry_leverage)
	print("=========interest ================")
	print(interest_coverage)
	month = ["Jan","Feb","Mar","April","May","June","July","Aug","Sept","Oct","Nov","Dec"]
	rep= []
	for (i,j,m,n) in zip(month,debt_of_assets,debt_to_enquiry_leverage,interest_coverage):
		rep.append([i,j,m,n])
	print("reports", rep)
	return columns, rep

def aboslute_value(value):	
	fin_abs= []
	for i in value:
		abs_val = abs(i)
		fin_abs.append(abs_val)

	return fin_abs

def get_result_with_filters(account, filters, account_details):

	year = int(frappe.defaults.get_user_default("fiscal_year"))
	account_res = []
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
		filters['presentation_currency'] = 'Ethiopia Birrr'
		filters['account_currency'] = 'Ethiopia Birrr'
		filters["account"] = account
		res = get_result(filters, account_details)
		account_res.append(res[-1]["balance"])

	return	account_res