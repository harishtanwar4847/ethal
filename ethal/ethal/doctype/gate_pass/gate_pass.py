# Copyright (c) 2021, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class GatePass(Document):
	def before_submit(self):
		self.approver_person = self.modified_by
		self.approver_date = self.modified
