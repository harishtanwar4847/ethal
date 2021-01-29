# -*- coding: utf-8 -*-
# Copyright (c) 2020, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ImportCostSheet(Document):
	def after_insert(self):
		
		sea_fright_etb = 0 
		inland_fright_etb = 0 
		insurance_etb = 0
		import_customs_duty_etb = 0
		other_etb = 0
		bank_charge_etb = 0
		storage_etb = 0
		port_handling_charge_etb = 0
		transit_and_clearing_etb = 0
		loading_and_unloading_etb = 0
		inland_transport_etb = 0
		miscellaneous_etb = 0

		for i in self.import_cost_sheet_items:
			print(i.amount)
			if i.items == 'Sea Fright (ETB)' and i.amount is not None:
				sea_fright_etb = i.amount
			if i.items == 'Inland Fright (ETB)' and i.amount is not None:
				inland_fright_etb = i.amount 
			if i.items == 'Insurance (ETB)' and i.amount is not None:
				insurance_etb = i.amount 
			if i.items == 'Import Customs Duty (ETB)' and i.amount is not None:
				import_customs_duty_etb = i.amount
			if i.items == 'Other (ETB)' and i.amount is not None:
				other_etb = i.amount 
			if i.items == 'Bank charge (ETB)' and i.amount is not None:
				bank_charge_etb = i.amount
			if i.items == 'Storage (ETB)' and i.amount is not None:
				storage_etb = i.amount
			if i.items == 'Port handling charge (ETB)' and i.amount is not None:
				port_handling_charge_etb = i.amount
			if i.items == 'Transit and clearing (ETB)' and i.amount is not None: 
				transit_and_clearing_etb = i.amount
			if i.items == 'Loading & unloading (ETB)' and i.amount is not None:
				loading_and_unloading_etb = i.amount
			if i.items == 'Inland transport (ETB)' and i.amount is not None:
				inland_transport_etb = i.amount 
			if i.items == 'Miscellaneous (ETB)' and i.amount is not None:
				miscellaneous_etb = i.amount 
 
		for j in self.import_cost_sheet_details:
			j.amount__etb_ = j.amount * self.exchange_rate if j.amount else 0
			j.sea_fright_etb = (sea_fright_etb/self.usd_value)*j.amount if j.amount else 0
			j.inland_fright_etb = (inland_fright_etb/self.usd_value)*j.amount if j.amount else 0
			j.insurance_etb = (insurance_etb/self.usd_value)*j.amount if j.amount else 0
			j.import_customs_duty_etb = (import_customs_duty_etb/self.usd_value)*j.amount if j.amount else 0 
			j.other_etb = (other_etb/self.usd_value)*j.amount if j.amount else 0
			j.bank_charge_etb = (bank_charge_etb/self.usd_value)*j.amount if j.amount else 0 
			j.storage_etb = (storage_etb/self.usd_value)*j.amount if j.amount else 0
			j.port_handling_charge_etb = (port_handling_charge_etb/self.usd_value)*j.amount if j.amount else 0
			j.transit_and_clearing_etb = (transit_and_clearing_etb/self.usd_value)*j.amount if j.amount else 0
			j.loading_and_unloading_etb = (loading_and_unloading_etb/self.usd_value)*j.amount if j.amount else 0
			j.inland_transport_etb = (inland_transport_etb/self.usd_value)*j.amount if j.amount else 0
			j.miscellaneous_etb = (miscellaneous_etb/self.usd_value)*j.amount if j.amount else 0
			j.total_actual_cost =  j.amount__etb_ + j.sea_fright_etb+j.inland_fright_etb+j.insurance_etb+j.import_customs_duty_etb+j.other_etb+j.bank_charge_etb+j.storage_etb+j.port_handling_charge_etb+j.transit_and_clearing_etb+j.loading_and_unloading_etb+j.inland_transport_etb+j.miscellaneous_etb 
			j.grand_total_cost_etb = j.total_actual_cost + j.customs_valuation_difference_etb if j.customs_valuation_difference_etb else 0
			j.unit_cost_per_kg_etb = j.grand_total_cost_etb / j.qty
			j.save()

	def before_save(self):
		
		sea_fright_etb = 0 
		inland_fright_etb = 0 
		insurance_etb = 0
		import_customs_duty_etb = 0
		other_etb = 0
		bank_charge_etb = 0
		storage_etb = 0
		port_handling_charge_etb = 0
		transit_and_clearing_etb = 0
		loading_and_unloading_etb = 0
		inland_transport_etb = 0
		miscellaneous_etb = 0

		for i in self.import_cost_sheet_items:
			print(i.amount)
			if i.items == 'Sea Fright (ETB)' and i.amount is not None:
				sea_fright_etb = i.amount
			if i.items == 'Inland Fright (ETB)' and i.amount is not None:
				inland_fright_etb = i.amount 
			if i.items == 'Insurance (ETB)' and i.amount is not None:
				insurance_etb = i.amount 
			if i.items == 'Import Customs Duty (ETB)' and i.amount is not None:
				import_customs_duty_etb = i.amount
			if i.items == 'Other (ETB)' and i.amount is not None:
				other_etb = i.amount 
			if i.items == 'Bank charge (ETB)' and i.amount is not None:
				bank_charge_etb = i.amount
			if i.items == 'Storage (ETB)' and i.amount is not None:
				storage_etb = i.amount
			if i.items == 'Port handling charge (ETB)' and i.amount is not None:
				port_handling_charge_etb = i.amount
			if i.items == 'Transit and clearing (ETB)' and i.amount is not None: 
				transit_and_clearing_etb = i.amount
			if i.items == 'Loading & unloading (ETB)' and i.amount is not None:
				loading_and_unloading_etb = i.amount
			if i.items == 'Inland transport (ETB)' and i.amount is not None:
				inland_transport_etb = i.amount 
			if i.items == 'Miscellaneous (ETB)' and i.amount is not None:
				miscellaneous_etb = i.amount 
 
		for j in self.import_cost_sheet_details:
			j.amount__etb_ = j.amount * self.exchange_rate if j.amount and self.exchange_rate else 0
			j.sea_fright_etb = (sea_fright_etb/self.usd_value)*j.amount if j.amount and self.usd_value else 0
			j.inland_fright_etb = (inland_fright_etb/self.usd_value)*j.amount if j.amount and self.usd_value else 0
			j.insurance_etb = (insurance_etb/self.usd_value)*j.amount if j.amount and self.usd_value else 0
			j.import_customs_duty_etb = (import_customs_duty_etb/self.usd_value)*j.amount if j.amount and self.usd_value else 0 
			j.other_etb = (other_etb/self.usd_value)*j.amount if j.amount and self.usd_value else 0
			j.bank_charge_etb = (bank_charge_etb/self.usd_value)*j.amount if j.amount and self.usd_value else 0 
			j.storage_etb = (storage_etb/self.usd_value)*j.amount if j.amount and self.usd_value else 0
			j.port_handling_charge_etb = (port_handling_charge_etb/self.usd_value)*j.amount if j.amount and self.usd_value else 0
			j.transit_and_clearing_etb = (transit_and_clearing_etb/self.usd_value)*j.amount if j.amount and self.usd_value else 0
			j.loading_and_unloading_etb = (loading_and_unloading_etb/self.usd_value)*j.amount if j.amount and self.usd_value else 0
			j.inland_transport_etb = (inland_transport_etb/self.usd_value)*j.amount if j.amount and self.usd_value else 0
			j.miscellaneous_etb = (miscellaneous_etb/self.usd_value)*j.amount if j.amount and self.usd_value else 0
			j.total_actual_cost =  j.amount__etb_ + j.sea_fright_etb+j.inland_fright_etb+j.insurance_etb+j.import_customs_duty_etb+j.other_etb+j.bank_charge_etb+j.storage_etb+j.port_handling_charge_etb+j.transit_and_clearing_etb+j.loading_and_unloading_etb+j.inland_transport_etb+j.miscellaneous_etb 
			j.grand_total_cost_etb = j.total_actual_cost + j.customs_valuation_difference_etb if j.customs_valuation_difference_etb else 0
			j.unit_cost_per_kg_etb = j.grand_total_cost_etb / j.qty
			# j.save()


@frappe.whitelist()
def get_value(name):
	return frappe.db.get_all('Purchase Receipt Item', filters={'parent': name}, fields=['*'], order_by='idx')