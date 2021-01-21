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
			print(i.items)
			if i.items == 'Sea Fright (ETB)':
				sea_fright_etb = i.amount
			if i.items == 'Inland Fright (ETB)':
				inland_fright_etb = i.amount 
			if i.items == 'Insurance (ETB)':
				insurance_etb = i.amount 
			if i.items == 'Import Customs Duty (ETB)':
				import_customs_duty_etb = i.amount
			if i.items == 'Other (ETB)':
				other_etb = i.amount 
			if i.items == 'Bank charge (ETB)':
				bank_charge_etb = i.amount
			if i.items == 'Storage (ETB)':
				storage_etb = i.amount
			if i.items == 'Port handling charge (ETB)':
				port_handling_charge_etb = i.amount
			if i.items == 'Transit and clearing (ETB)':
				transit_and_clearing_etb = i.amount
			if i.items == 'Loading & unloading (ETB)':
				loading_and_unloading_etb = i.amount
			if i.items == 'Inland transport (ETB)':
				inland_transport_etb = i.amount 
			if i.items == 'Miscellaneous (ETB)':
				miscellaneous_etb = i.amount 
 
		for j in self.import_cost_sheet_details:
			j.amount__etb_ = j.amount * self.exchange_rate
			j.sea_fright_etb = (sea_fright_etb/self.usd_value)*j.amount 
			j.inland_fright_etb = (inland_fright_etb/self.usd_value)*j.amount
			j.insurance_etb = (insurance_etb/self.usd_value)*j.amount
			j.import_customs_duty_etb = (import_customs_duty_etb/self.usd_value)*j.amount 
			j.other_etb = (other_etb/self.usd_value)*j.amount 
			j.bank_charge_etb = (bank_charge_etb/self.usd_value)*j.amount 
			j.storage_etb = (storage_etb/self.usd_value)*j.amount 
			j.port_handling_charge_etb = (port_handling_charge_etb/self.usd_value)*j.amount 
			j.transit_and_clearing_etb = (transit_and_clearing_etb/self.usd_value)*j.amount 
			j.loading_and_unloading_etb = (loading_and_unloading_etb/self.usd_value)*j.amount 
			j.inland_transport_etb = (inland_fright_etb/self.usd_value)*j.amount 
			j.miscellaneous_etb = (miscellaneous_etb/self.usd_value)*j.amount 
			j.save()


@frappe.whitelist()
def get_value(name):
	return frappe.db.get_all('Purchase Invoice Item', {'parent': name}, ['*'])