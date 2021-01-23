# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	columns = ['Items:Data:300','Amount (USD):Float:150', 'Amount ( ETB ):Float:150', 'Sea Fright (ETB):Float:150', 'Inland Fright (ETB):Float:150', 'Insurance (ETB):Float:150', 'Import Customs Duty (ETB):Float:150', 'Other (ETB):Float:150', 'Bank charge (ETB):Flaot:150', 'Storage (ETB):Float:150', 'Port handling charge (ETB):Float:150', 'Transit and clearing (ETB):Float:150', 'Loading and unloading (ETB):Float:150', 'Inland transport (ETB):Float:150', 'Miscellaneous (ETB):Float:150', 'Total:Float:150']
	data = get_data(filters)
	print(data)
	return columns, data


def get_data(filters):
	return frappe.db.sql("""
		select item_name,amount, amount__etb_, sea_fright_etb, inland_fright_etb, insurance_etb, import_customs_duty_etb, other_etb, 
			bank_charge_etb, storage_etb, port_handling_charge_etb, transit_and_clearing_etb, loading_and_unloading_etb, 
			inland_transport_etb, miscellaneous_etb, total from `tabImport Cost Sheet Details` where parent = '{0}'
	""".format(filters.import_cost_sheet), as_list=True)
