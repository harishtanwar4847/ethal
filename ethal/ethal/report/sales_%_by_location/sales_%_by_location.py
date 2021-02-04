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

	columns = ["Month::180"]+["DB sales %::180"]+["TU sales %::180"]
	
	# res_data_50000_total = result_data_total("50000 - Direct Costs - ETL",filters, account_details)
	res_data_41110_total = []
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
		filters["account"] = "41110 - Debre Birhan - ETL"
		res = get_result(filters, account_details)
		res_data_41110_total.append(res[-2]["balance"])

	res_data_41100_total = []
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
		filters["account"] = "41100 - Aluminum Utensil Sales - ETL"
		res = get_result(filters, account_details)
		res_data_41100_total.append(res[-2]["balance"])

	res_data_41120_total = []
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
		filters["account"] = "41120 - Tulefa - ETL"
		res = get_result(filters, account_details)
		res_data_41120_total.append(res[-2]["balance"])

	


	
	du_sales = [(b / m)*100 if m != 0 and b!=0 else 0 for b,m in zip(res_data_41110_total, res_data_41100_total)]
	du_sales = absolute_value(du_sales)

	tu_sales = [(b / m)*100 if m != 0 and b!=0 else 0 for b,m in zip(res_data_41120_total, res_data_41100_total)]
	tu_sales = absolute_value(tu_sales)

	month = ["Jan","Feb","Mar","April","May","June","July","Aug","Sept","Oct","Nov","Dec"]
	rep= []
	for (a,b,c) in zip(month,du_sales,tu_sales):
		rep.append([a,b,c])

	return columns, rep



def absolute_value(val):
	fin_abs= []
	for i in val:
		abs_val = abs(i)
		fin_abs.append(abs_val)

	return fin_abs
