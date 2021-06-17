# -*- coding: utf-8 -*-
# Copyright (c) 2021, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
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

class EOSWeeklyScorecard(Document):
	def validate(self):
		for idx, val in enumerate(self.eos_details):
			if val.parameter == 'Achieved':
				a= val.idx - 2
				previous_values = self.eos_details[a].actual / self.eos_details[a].target if self.eos_details[a].actual and self.eos_details[a].target else 0
				val.actual = previous_values * 100
				
			if val.division == 'UD-TU' and val.parameter == 'Despatch - Utensils':
				sales_invoice = frappe.db.get_all('Sales Invoice', filters={'posting_date': [ 'between', [self.from_date, self.to_date]], 'naming_series': ['like', '%'+'TU'+'%'], 'docstatus': 1 }, fields=['name'])	
				net_weight_total = 0
				if sales_invoice:
					for i in sales_invoice:
						net_weight_amount = frappe.db.sql("""
							select sum(si.total_net_weight) 
							from `tabSales Invoice Item` as si
							join `tabItem` as i
							on si.item_code =  i.name
							where i.item_group = 'FINISHED GOODS' and si.parent = '{0}'
						""".format(i['name']))
						net_weight_total += net_weight_amount[0][0] if net_weight_amount[0][0] != None else 0
				val.actual = net_weight_total /1000	

			if val.division == 'UD-DB' and val.parameter == 'Despatch - Utensils':
				sales_invoice = frappe.db.get_all('Sales Invoice', filters={'posting_date': [ 'between', [self.from_date, self.to_date]], 'naming_series': ['like', '%'+'DB'+'%'], 'docstatus': 1 }, fields=['name'])	
				net_weight_total = 0
				if sales_invoice:
					for i in sales_invoice:
						net_weight_amount = frappe.db.sql("""
							select sum(si.total_net_weight) 
							from `tabSales Invoice Item` as si
							join `tabItem` as i
							on si.item_code =  i.name
							where i.item_group = 'FINISHED GOODS' and si.parent = '{0}' 
						""".format(i['name']))
						net_weight_total += net_weight_amount[0][0] if net_weight_amount[0][0] != None else 0
				val.actual = net_weight_total /1000	

			if val.parameter == 'Sales Price':
				net_weight_total = 0
				sales_invoice_weight = frappe.db.sql("""
					select sum(sii.total_net_weight)
					from `tabSales Invoice Item` as sii
					join `tabSales Invoice` as si
					on si.name = sii.parent
					join `tabItem` as i
					on sii.item_code =  i.name
					where i.item_group = 'FINISHED GOODS' and si.posting_date between '{0}' and '{1}' and si.docstatus = 1
				""".format(self.from_date, self.to_date))
				if sales_invoice_weight:
					net_weight_total += sales_invoice_weight[0][0] if sales_invoice_weight[0][0] != None else 0
				sales_invoice_price = frappe.db.sql("""
					select sum(sii.amount)
					from `tabSales Invoice Item` as sii
					join `tabSales Invoice` as si
					on si.name = sii.parent
					where si.posting_date between '{0}' and '{1}' and si.docstatus = 1
				""".format(self.from_date, self.to_date))
				price = 0
				if sales_invoice_price:
					price += sales_invoice_price[0][0] if sales_invoice_price[0][0] != None else 0
				val.actual = price / net_weight_total if net_weight_total != 0 else 0

			if val.parameter == 'Cash Balance':
				print(self.from_date)
				print(self.to_date)
				year = frappe.defaults.get_user_default("fiscal_year")
				a = calculate('11100 - Cash and Bank - E21', year, self.from_date, self.to_date)
				val.actual = a

@frappe.whitelist()
def get_previous_record(doc):
	get_parent = frappe.db.get_all('EOS Weekly Scorecard', ['name'], order_by='name desc', page_length=1)
	if get_parent:
		get_previous_record = frappe.db.get_all('EOS Weekly Scorecard Details', {'parent': get_parent[0]['name']}, ['*'], order_by='idx asc')
		return get_previous_record
 
def calculate(account, year, from_date, to_date):
	account_details = {}
	
	for acc in frappe.db.sql("""select name, is_group from tabAccount""", as_dict=1):
		account_details.setdefault(acc.name, acc)

	filters = frappe._dict({
			'company': 'Ethal 2021', 
			'from_date': from_date, 
			'to_date': to_date, 
			'group_by': 'Group by Voucher (Consolidated)', 
			'show_opening_entries': 1, 
			'include_default_book_entries': 1
			})
		
	validate_filters(filters, account_details)

	validate_party(filters)

	filters = set_account_currency(filters)

	filters["account"] = account
	res = get_result(filters, account_details)
	
	return res[-1]['balance']