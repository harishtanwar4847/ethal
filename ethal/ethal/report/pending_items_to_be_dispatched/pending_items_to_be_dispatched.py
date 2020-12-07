# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data

def execute(filters=None):
	columns, data = [], []
	columns = get_column()
	data = get_data()
	return columns, data

def get_column():
    columns = ["Customer ::150"]+["Sales Order No ::150"]+["Item ::150"]+["Ordered Qty ::250"]+["Delivered Qty ::150"]+["Pending Qty ::150"]
    return columns

def get_data():

	return frappe.db.sql("""
	select si.customer, sii.sales_order, sii.item_code, sii.stock_qty, sii.delivered_qty, (sii.stock_qty - sii.delivered_qty) 
	from `tabSales Invoice` as si 
	left join `tabSales Invoice Item` as sii
	on si.name = sii.parent;
	""")