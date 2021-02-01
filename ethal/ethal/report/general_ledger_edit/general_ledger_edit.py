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

	columns = ["Month::180"]+["Current/working Capital::180"]+["Quick(Acid)::180"]
	res_data_11000 = []
	
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
		filters["account"] = "11000 - Current Assets - ETL"
		res = get_result(filters, account_details)
		res_data_11000.append(res[-1]["balance"])

	res_data_21000 = []

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
		filters["account"] = "21000 - Current Liabilities - ETL"
		res = get_result(filters, account_details)
		res_data_21000.append(res[-1]["balance"])

	res_data_11500 = []

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
		filters["account"] = "11500 - Stock Assets - ETL"
		res = get_result(filters, account_details)
		res_data_11500.append(res[-1]["balance"])

	res_data_11500 = []

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
		filters["account"] = "11500 - Stock Assets - ETL"
		res = get_result(filters, account_details)
		res_data_11500.append(res[-1]["balance"])

	res_data_21500 = []

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
		filters["account"] = "21500 - Stock Liabilities - ETL"
		res = get_result(filters, account_details)
		res_data_21500.append(res[-1]["balance"])

	total_current_assets = [b - m  for b,m in zip(res_data_11000, res_data_11500)]
	total_current_liability = [b - m  for b,m in zip(res_data_21000, res_data_21500)]
	quick = [b / m if m != 0 and b!=0 else 0 for b,m in zip(total_current_assets, total_current_liability)]
	quick = aboslute_value(quick)
	print("11000 ==> ",res_data_11000)
	print("21000 ==> ",res_data_21000)
	total_working_capital = [b / m if m != 0 and b!=0 else 0 for b,m in zip(res_data_11000, res_data_21000)]
	total_working_capital = aboslute_value(total_working_capital)
	month = ["Jan","Feb","Mar","April","May","June","July","Aug","Sept","Oct","Nov","Dec"]
	rep= []
	for (i,j,m) in zip(month,total_working_capital,quick):
		rep.append([i,j,m])
	print(rep)
	return columns, rep

def aboslute_value(value):	
	fin_abs= []
	for i in value:
		abs_val = abs(i)
		fin_abs.append(abs_val)

	return fin_abs
