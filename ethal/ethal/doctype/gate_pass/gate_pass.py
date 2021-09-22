# Copyright (c) 2021, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class GatePass(Document):
	def before_submit(self):
		self.approver_person = self.modified_by
		self.approver_date = self.modified

@frappe.whitelist()
def get_delivery_note_items(name):
	delivery_note_item = frappe.get_all('Delivery Note Item', filters={'parent': name}, fields=['*'])
	for i in delivery_note_item:
		return i