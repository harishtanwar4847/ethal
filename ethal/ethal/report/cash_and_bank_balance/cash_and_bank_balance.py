# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr
from erpnext.accounts.report.financial_statements \
	import filter_accounts, set_gl_entries_by_account, filter_out_zero_value_rows
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import get_accounting_dimensions, get_dimension_with_children

value_fields = ("opening_debit", "opening_credit", "debit", "credit", "closing_debit", "closing_credit")

def execute(filters=None):
	validate_filters(filters)
	data = get_data(filters)
	columns = get_columns()
	return columns, data

def validate_filters(filters):
	if not filters.fiscal_year:
		frappe.throw(_("Fiscal Year {0} is required").format(filters.fiscal_year))

	fiscal_year = frappe.db.get_value("Fiscal Year", filters.fiscal_year, ["year_start_date", "year_end_date"], as_dict=True)
	if not fiscal_year:
		frappe.throw(_("Fiscal Year {0} does not exist").format(filters.fiscal_year))
	else:
		filters.year_start_date = getdate(fiscal_year.year_start_date)
		filters.year_end_date = getdate(fiscal_year.year_end_date)

	if not filters.from_date:
		filters.from_date = filters.year_start_date

	if not filters.to_date:
		filters.to_date = filters.year_end_date

	filters.from_date = getdate(filters.from_date)
	filters.to_date = getdate(filters.to_date)

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date cannot be greater than To Date"))

	if (filters.from_date < filters.year_start_date) or (filters.from_date > filters.year_end_date):
		frappe.msgprint(_("From Date should be within the Fiscal Year. Assuming From Date = {0}")\
			.format(formatdate(filters.year_start_date)))

		filters.from_date = filters.year_start_date

	if (filters.to_date < filters.year_start_date) or (filters.to_date > filters.year_end_date):
		frappe.msgprint(_("To Date should be within the Fiscal Year. Assuming To Date = {0}")\
			.format(formatdate(filters.year_end_date)))
		filters.to_date = filters.year_end_date

def get_data(filters):
	# print("account filter ===========>",filters.account)
	
	# accounts = frappe.db.sql("""select name, account_number, parent_account, account_name, root_type, report_type, lft, rgt

	# 	from `tabAccount` where company=%s  order by lft""", filters.company, as_dict=True)
	if filters.account:
		# print("size of filter is ==> ",len(filters.account))
		
		tup = tuple(filters.account)
		account_list = []
		def account_traversing(account):
			if account.is_group == 1:
				account_list.append(account)
				child_accounts_query = """select name, account_number, parent_account, account_name, root_type, report_type, lft, rgt, is_group
											from `tabAccount` where company= '{}' and parent_account = '{}' order by account_number,lft""".format(filters.company,account.name)
				child_accounts = frappe.db.sql(child_accounts_query, as_dict=True)
				# print("child_accounts ======> ", child_accounts)
				for c_account in child_accounts:
					account_traversing(c_account)
			else:
				account_list.append(account)

		for selected_account in filters.account:
			selected_accounts_query = """select name, account_number, parent_account, account_name, root_type, report_type, lft, rgt, is_group
											from `tabAccount` where company= '{}' and name = '{}' order by account_number,lft""".format(filters.company,selected_account)
			selected_accounts = frappe.db.sql(selected_accounts_query, as_dict=True)
			selected_accounts[0].parent_account= None
			# print("selected_account ===> ",selected_account)
			account_traversing(selected_accounts[0])
			# print("account_list -======> ",account_list)
		
	else:
		account_list = frappe.db.sql("""select name, account_number, parent_account, account_name, root_type, report_type, lft, rgt

	 	from `tabAccount` where company=%s order by lft """, filters.company, as_dict=True)

	# print("accounts ==> ", accounts)
	company_currency = erpnext.get_company_currency(filters.company)
	if not account_list:
		return None

	accounts, accounts_by_name, parent_children_map = filter_accounts(account_list)
	# print("accounts after filter_accounts =======> ",accounts)
	# print("accounts_by_name ========> ",accounts_by_name)
	# print("parent_children_map ======> ",parent_children_map)
	# print("==================== Account print start ===================")
	# print(accounts)
	# print("===================Account Print end =======================")
	min_lft, max_rgt = frappe.db.sql("""select min(lft), max(rgt) from `tabAccount`
		where company=%s""", (filters.company,))[0]

	gl_entries_by_account = {}

	opening_balances = get_opening_balances(filters)
	#add filter inside list so that the query in financial_statements.py doesn't break
	if filters.project:
		filters.project = [filters.project]

	set_gl_entries_by_account(filters.company, filters.from_date,
		filters.to_date, min_lft, max_rgt, filters, gl_entries_by_account, ignore_closing_entries=not flt(filters.with_period_closing_entry))

	# print("accounts before total_row =====> ",accounts)
	# print("gl_entries_by_account before total_row =====> ",gl_entries_by_account)
	# print("opening_balances before total_row =====> ",opening_balances)
	# print("accounts before total_row =====> ",accounts)
	total_row = calculate_values(accounts, gl_entries_by_account, opening_balances, filters, company_currency)
	# print("total row =====> ",total_row)
	# print("gl_entries_by account after total_row ===================> ",gl_entries_by_account)
	accumulate_values_into_parents(accounts, accounts_by_name)

	data = prepare_data(accounts, filters, total_row, parent_children_map, company_currency)
	# print("data after prepaer_data =======> ",data)
	data = filter_out_zero_value_rows(data, parent_children_map, show_zero_values=filters.get("show_zero_values"))
	# print("data after filter_out_zero_value_rows =====> ",data)
	return data

def get_opening_balances(filters):
	# print("inside get_opening_balances")
	balance_sheet_opening = get_rootwise_opening_balances(filters, "Balance Sheet")
	pl_opening = get_rootwise_opening_balances(filters, "Profit and Loss")

	balance_sheet_opening.update(pl_opening)
	# print("o/p of get_opening_balances  ===> ",balance_sheet_opening)
	return balance_sheet_opening


def get_rootwise_opening_balances(filters, report_type):
	# print("inside get_rootwise_opening_balances")
	# print("filters ========> ", filters)
	additional_conditions = ""
	if not filters.show_unclosed_fy_pl_balances:
		additional_conditions = " and posting_date >= %(year_start_date)s" \
			if report_type == "Profit and Loss" else ""

	if not flt(filters.with_period_closing_entry):
		additional_conditions += " and ifnull(voucher_type, '')!='Period Closing Voucher'"

	if filters.cost_center:
		lft, rgt = frappe.db.get_value('Cost Center', filters.cost_center, ['lft', 'rgt'])
		additional_conditions += """ and cost_center in (select name from `tabCost Center`
			where lft >= %s and rgt <= %s)""" % (lft, rgt)

	if filters.project:
		additional_conditions += " and project = %(project)s"

	if filters.finance_book:
		fb_conditions = " AND finance_book = %(finance_book)s"
		if filters.include_default_book_entries:
			fb_conditions = " AND (finance_book in (%(finance_book)s, %(company_fb)s, '') OR finance_book IS NULL)"

		additional_conditions += fb_conditions

	accounting_dimensions = get_accounting_dimensions(as_list=False)
	# print("accounting_dimensions =====> ",accounting_dimensions)

	query_filters = {
		"company": filters.company,
		"from_date": filters.from_date,
		"report_type": report_type,
		"year_start_date": filters.year_start_date,
		"project": filters.project,
		"finance_book": filters.finance_book,
		"company_fb": frappe.db.get_value("Company", filters.company, 'default_finance_book'),
		"account_type": "Cash"
	}

	if accounting_dimensions:
		for dimension in accounting_dimensions:
			if filters.get(dimension.fieldname):
				if frappe.get_cached_value('DocType', dimension.document_type, 'is_tree'):
					filters[dimension.fieldname] = get_dimension_with_children(dimension.document_type,
						filters.get(dimension.fieldname))
					additional_conditions += "and {0} in %({0})s".format(dimension.fieldname)
				else:
					additional_conditions += "and {0} in (%({0})s)".format(dimension.fieldname)

				query_filters.update({
					dimension.fieldname: filters.get(dimension.fieldname)
				})

	gle = frappe.db.sql("""
		select
			account, sum(debit) as opening_debit, sum(credit) as opening_credit
		from `tabGL Entry`
		where
			company=%(company)s
			{additional_conditions}
			and (posting_date < %(from_date)s or ifnull(is_opening, 'No') = 'Yes')
			and account in (select name from `tabAccount` where report_type=%(report_type)s and account_type=%(account_type)s)
		group by account""".format(additional_conditions=additional_conditions), query_filters , as_dict=True,)

	opening = frappe._dict()
	# print("GLE YAHA HAI =====> ",gle)
	for d in gle:
		opening.setdefault(d.account, d)
	# print("o/p of get_rootwise_opening_balances ======> ",opening)
	return opening

def calculate_values(accounts, gl_entries_by_account, opening_balances, filters, company_currency):
	# print("inside calculate_values")
	init = {
		"opening_debit": 0.0,
		"opening_credit": 0.0,
		"debit": 0.0,
		"credit": 0.0,
		"closing_debit": 0.0,
		"closing_credit": 0.0
	}

	total_row = {
		"account": "'" + _("Total") + "'",
		"account_name": "'" + _("Total") + "'",
		"warn_if_negative": True,
		"opening_debit": 0.0,
		"opening_credit": 0.0,
		"debit": 0.0,
		"credit": 0.0,
		"closing_debit": 0.0,
		"closing_credit": 0.0,
		"parent_account": None,
		"indent": 0,
		"has_value": True,
		"currency": company_currency
	}

	# print("accounts is ==> ",accounts)
	# query = """all (non-group) child accounts for input account name in filter"""
	for d in accounts:
		# print("======== inside accounts for loop =====")
		d.update(init.copy())

		# add opening
		# d["opening_debit"] = opening_balances.get(d.name, {}).get("opening_debit", 0)
		# print("""d["opening_debit"]  ======> """,d["opening_debit"])
		# d["opening_credit"] = opening_balances.get(d.name, {}).get("opening_credit", 0)
		# print("""d["opening_credit"]  ======> """,d["opening_credit"])

		for entry in gl_entries_by_account.get(d.name, []):
			# print("Entry =====> ",entry)
			if cstr(entry.is_opening) != "Yes":
				d["debit"] += flt(entry.debit)
				d["credit"] += flt(entry.credit)

		d["closing_debit"] = d["opening_debit"] + d["debit"]
		d["closing_credit"] = d["opening_credit"] + d["credit"]

		prepare_opening_closing(d)

		for field in value_fields:
			# print("d[field] ==> ",d[field])
			# print("total_row[field] ==> ",total_row[field])
			total_row[field] += d[field]

	return total_row

def accumulate_values_into_parents(accounts, accounts_by_name):
	for d in reversed(accounts):
		if d.parent_account:

			for key in value_fields:
				accounts_by_name[d.parent_account][key] += d[key]

def prepare_data(accounts, filters, total_row, parent_children_map, company_currency):
	data = []

	for d in accounts:
		# Prepare opening closing for group account
		if parent_children_map.get(d.account):
			prepare_opening_closing(d)

		has_value = False
		row = {
			"account": d.name,
			"parent_account": d.parent_account,
			"indent": d.indent,
			"from_date": filters.from_date,
			"to_date": filters.to_date,
			"currency": company_currency,
			"account_name": ('{} - {}'.format(d.account_number, d.account_name)
				if d.account_number else d.account_name)
		}

		for key in value_fields:
			row[key] = flt(d.get(key, 0.0), 3)

			if abs(row[key]) >= 0.005:
				# ignore zero values
				has_value = True

		row["has_value"] = has_value
		data.append(row)

	data.extend([{},total_row])

	return data

def get_columns():
	return [
		{
			"fieldname": "account",
			"label": _("Account"),
			"fieldtype": "Link",
			"options": "Account",
			"width": 300
		},
		{
			"fieldname": "currency",
			"label": _("Currency"),
			"fieldtype": "Link",
			"options": "Currency",
			"hidden": 1
		},
		{
			"fieldname": "opening_debit",
			"label": _("Opening (Dr)"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "opening_credit",
			"label": _("Opening (Cr)"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "debit",
			"label": _("Debit"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "credit",
			"label": _("Credit"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "closing_debit",
			"label": _("Closing (Dr)"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "closing_credit",
			"label": _("Closing (Cr)"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		}
	]

def prepare_opening_closing(row):
	# print("inside prepare_opening_closing")
	# print("ROW =======> ",row)
	dr_or_cr = "debit" if row["root_type"] in ["Asset", "Equity", "Expense"] else "credit"
	reverse_dr_or_cr = "credit" if dr_or_cr == "debit" else "debit"

	for col_type in ["opening", "closing"]:
		valid_col = col_type + "_" + dr_or_cr
		reverse_col = col_type + "_" + reverse_dr_or_cr
		row[valid_col] -= row[reverse_col]
		if row[valid_col] < 0:
			row[reverse_col] = abs(row[valid_col])
			row[valid_col] = 0.0
		else:
			row[reverse_col] = 0.0