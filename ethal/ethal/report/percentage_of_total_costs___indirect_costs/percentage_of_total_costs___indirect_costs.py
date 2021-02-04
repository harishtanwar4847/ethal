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

	columns = ["Month::180"]+["Manpower cost - HO/Total sales::180"]+["Financial costs - HO/Total sales::180"]+["General & Admin Expenses - HO/Total sales::180"]+["Non Operational HO/Total sales::180"]
	
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
		filters["account"] = "50000 - Direct Costs - ETL"
		res = get_result(filters, account_details)
		res_data_50000_total.append(res[-2]["balance"])

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
		filters['presentation_currency'] = 'Ethiopia Birrr'
		filters['account_currency'] = 'Ethiopia Birrr'
		filters["from_date"] = first_date
		filters["to_date"] = last_date
		filters["account"] = "60000 - Indirect Costs - ETL"
		res = get_result(filters, account_details)
		res_data_60000_total.append(res[-2]["balance"])

	res_data_61000_total = []
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
		filters["account"] = "61000 - Salary and benefits - ETL"
		res = get_result(filters, account_details)
		res_data_61000_total.append(res[-2]["balance"])

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
		filters['presentation_currency'] = 'Ethiopia Birrr'
		filters['account_currency'] = 'Ethiopia Birrr'
		filters["from_date"] = first_date
		filters["to_date"] = last_date
		filters["account"] = "62000 - Financial expenses - ETL"
		res = get_result(filters, account_details)
		res_data_62000_total.append(res[-2]["balance"])

	res_data_63000_total = []
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
		filters["account"] = "63000 - General and Admin Expenses - ETL"
		res = get_result(filters, account_details)
		res_data_63000_total.append(res[-2]["balance"])

	res_data_64000_total = []
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
		filters["account"] = "64000 - Non-Operational exp - ETL"
		res = get_result(filters, account_details)
		res_data_64000_total.append(res[-2]["balance"])

	
	mpc = [b / (m-c) if m-c!= 0 and b!=0 else 0 for b,m,c in zip(res_data_61000_total, res_data_50000_total,res_data_60000_total)]
	mpc = absolute_value(mpc)	

	fc = [b / (m-c) if m-c!= 0 and b!=0 else 0 for b,m,c in zip(res_data_62000_total, res_data_50000_total,res_data_60000_total)]
	fc = absolute_value(fc)

	general_and_admin_expenses = [b / (m-c) if m-c!= 0 and b!=0 else 0 for b,m,c in zip(res_data_63000_total, res_data_50000_total,res_data_60000_total)]
	general_and_admin_expenses = absolute_value(general_and_admin_expenses)

	non_operational_ho = [b / (m-c) if m-c!= 0 and b!=0 else 0 for b,m,c in zip(res_data_64000_total, res_data_50000_total,res_data_60000_total)] 	
	non_operational_ho = absolute_value(non_operational_ho)

	month = ["Jan","Feb","Mar","April","May","June","July","Aug","Sept","Oct","Nov","Dec"]
	rep= []
	for (a,b,c,d,e) in zip(month,mpc,fc,general_and_admin_expenses,non_operational_ho):
		rep.append([a,b,c,d,e])

	return columns, rep



def absolute_value(val):
	fin_abs= []
	for i in val:
		abs_val = abs(i)
		fin_abs.append(abs_val)

	return fin_abs
