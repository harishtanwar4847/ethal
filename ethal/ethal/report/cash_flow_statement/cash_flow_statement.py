# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	columns = ["Account::280"]+["ETB::300"]
	data = get_data(filters)
	return columns, data

def cash_flows_operating_activities():
	return {'Account': 'Cash flows from operating activities', 'ETB': ''}

def cash_receipt_from_customer(party_type, payment_type, from_date, to_date):
	a = get_payment_entry_value(party_type, payment_type, from_date, to_date)
	print(a)
	return {'Account': 'Cash receipts from customers', 'ETB': a}

def get_payment_entry_value(party_type, payment_type, from_date, to_date):
	return frappe.db.sql(""" 
	select sum(paid_amount) from `tabPayment Entry` where party_type = '{}' and payment_type='{}' and (posting_date between '{}' and '{}')
	""".format(party_type, payment_type, from_date, to_date), as_list=1)[0][0]	

def get_data(filters):
	data_list = []

	cfoa = cash_flows_operating_activities()
	data_list.append(cfoa)

	crfc = cash_receipt_from_customer('Customer', 'Receive', filters.from_date, filters.to_date)
	data_list.append(crfc)

	return data_list
