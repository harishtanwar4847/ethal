# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	columns = ["Import Cost Sheet:Link/Import Cost Sheet:200"]+['Items:Data:250', 'Quantity:Float:80', 'Rate:Float:100', 'Amount (USD):Float:150', 'Amount ( ETB ):Float:150', 'Sea Fright (ETB):Float:150', 'Inland Fright (ETB):Float:150', 'Insurance (ETB):Float:150', 'Import Customs Duty (ETB):Float:150', 'Other (ETB):Float:150', 'Bank charge (ETB):Flaot:150', 'Storage (ETB):Float:150', 'Port handling charge (ETB):Float:150', 'Transit and clearing (ETB):Float:150', 'Loading and unloading (ETB):Float:150', 'Inland transport (ETB):Float:150', 'Miscellaneous (ETB):Float:150', 'Total Actual Cost:Float:150', 'Customs valuation difference (ETB):Float:150', 'Grand Total Cost (ETB):Float:150', 'Unit Cost per KG (ETB):Float:150']
	data = get_data(filters)
	print(data)
	return columns, data

def get_data(filters):
	if filters.import_cost_sheet:
		return frappe.db.sql("""
			select parent, item_name,qty,rate, amount, amount__etb_, sea_fright_etb, inland_fright_etb, insurance_etb, import_customs_duty_etb, other_etb, 
				bank_charge_etb, storage_etb, port_handling_charge_etb, transit_and_clearing_etb, loading_and_unloading_etb, 
				inland_transport_etb, miscellaneous_etb, total_actual_cost, (tax_1+tax_3+tax_4+tax_5+tax_15+tax_16), grand_total_cost_etb, unit_cost_per_kg_etb 
			from `tabImport Cost Sheet Details`
			where parent = '{0}'
			order by parent
		""".format(filters.import_cost_sheet), as_list=True)
	else:
		return frappe.db.sql("""
			select parent, item_name,qty,rate, amount, amount__etb_, sea_fright_etb, inland_fright_etb, insurance_etb, import_customs_duty_etb, other_etb, 
				bank_charge_etb, storage_etb, port_handling_charge_etb, transit_and_clearing_etb, loading_and_unloading_etb, 
				inland_transport_etb, miscellaneous_etb, total_actual_cost, (tax_1+tax_3+tax_4+tax_5+tax_15+tax_16), grand_total_cost_etb, unit_cost_per_kg_etb 
			from `tabImport Cost Sheet Details`
			order by parent
		""", as_list=True)