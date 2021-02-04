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
from ethal.ethal.report.solvency_ratios.solvency_ratios import get_result_with_filters

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

	columns = ["Month::180"]+["Direct material/Total sales ::180"]+["Fuel/Total sales::180"]+["Manpower Cost - Factory/Total sales::180"]+["Stores & Repairs/Total sales::180"]+["Utilities - Electricity & Water/Total sales::180"]
	res_data_51000_01 = get_result_with_filters('51000-01 - Direct Material - ETL', filters, account_details)
	res_data_51000_02 = get_result_with_filters('51000-02 - Material Handling-Circle-DB - ETL', filters, account_details)
	res_data_52000_01 = get_result_with_filters('52000-01 - Direct Material-UD-DB - ETL', filters, account_details)
	res_data_53000_01 = get_result_with_filters('53000-01 - Direct Material-UD-TU - ETL', filters, account_details)
	res_data_51000_03 = get_result_with_filters('51000-03 - Fuel-Diesel-Circle-DB - ETL', filters, account_details)
	res_data_51000_04 = get_result_with_filters('51000-04 - Direct Labour-Circle-DB - ETL', filters, account_details)
	res_data_52000_02 = get_result_with_filters('52000-02 - Direct Labour-UD-DB - ETL', filters, account_details)
	res_data_53000_02 = get_result_with_filters('53000-02 - Direct Labour-UD-TU - ETL', filters, account_details)
	res_data_54100 = get_result_with_filters('54100 - Wages ,Salaries and Benefits - ETL', filters, account_details)
	res_data_54200 = get_result_with_filters('54200 - Stores - ETL', filters, account_details)
	res_data_54300 = get_result_with_filters('54300 - Repairs and Maintenance - ETL', filters, account_details)
	res_data_54400 = get_result_with_filters('54400 - Utilities - ETL', filters, account_details)
	res_data_51000_05 = get_result_with_filters('51000-05 - Electricity Consumption - Circle - DB - ETL', filters, account_details)
	res_data_52000_04 = get_result_with_filters('52000-04 - Transportation for RM-UD - ETL', filters, account_details)
	res_data_53000_04 = get_result_with_filters('53000-04 - Electricity consumption -UD-TU - ETL', filters, account_details)
	res_data_50000 = get_result_with_filters('50000 - Direct Costs - ETL', filters, account_details)	
	res_data_60000 = get_result_with_filters('60000 - Indirect Costs - ETL', filters, account_details)

	addition_of_50000_and_60000 = [a+b for a,b in zip(res_data_50000,res_data_60000)]
	direct_material = [(a+b+c+d)/e  for a,b,c,d,e in zip(res_data_51000_01, res_data_51000_02, res_data_52000_01, res_data_53000_01,addition_of_50000_and_60000)]
	direct_material = aboslute_value(direct_material)
	print(db_sales)
	fuel = [(a/b) for a,b in zip(res_data_51000_03, addition_of_50000_and_60000)]
	fuel = aboslute_value(fuel)
	manpower_cost = [(a+b+c+d)/e  for a,b,c,d,e in zip(res_data_51000_04, res_data_52000_02, res_data_53000_02,res_data_54100, addition_of_50000_and_60000)]
	manpower_cost = aboslute_value(manpower_cost)
	stores_and_repairs = [(a+b)/c for a,b,c in zip(res_data_54200, res_data_54300, addition_of_50000_and_60000)]
	stores_and_repairs = aboslute_value(stores_and_repairs)
	utilities = [(a+b+c+d)/e  for a,b,c,d,e in zip(res_data_54400, res_data_51000_05, res_data_52000_04, res_data_53000_04,addition_of_50000_and_60000)]
	utilities = aboslute_value(utilities)
	month = ["Jan","Feb","Mar","April","May","June","July","Aug","Sept","Oct","Nov","Dec"]
	rep= []
	for (i,j,m) in zip(month,direct_material, fuel, manpower_cost, stores_and_repairs, utilities):
		rep.append([i,j,m,n,k,l])
	print("reports", rep)
	return columns, rep

def aboslute_value(value):	
	fin_abs= []
	for i in value:
		abs_val = abs(i)
		fin_abs.append(abs_val)

	return fin_abs