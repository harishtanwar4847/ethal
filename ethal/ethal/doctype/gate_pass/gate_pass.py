# Copyright (c) 2021, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class GatePass(Document):
	def before_submit(self):
		self.approver_person = self.modified_by
		self.approver_date = self.modified

@frappe.whitelist()
def get_party_details(party, party_type):
	_party_name = "title" if party_type in ("Student", "Shareholder") else party_type.lower() + "_name"
	return frappe.db.get_value(party_type, party, _party_name)

@frappe.whitelist()
def get_delivery_note_items(name):
	delivery_note_item = frappe.get_all('Delivery Note Item', filters={'parent': name}, fields=['*'])
	for i in delivery_note_item:
		return i