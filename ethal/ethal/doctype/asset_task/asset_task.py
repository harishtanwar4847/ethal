# Copyright (c) 2021, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import nowdate, getdate

class AssetTask(Document):
	def validate(self):
		if getdate(self.due_date) < getdate(nowdate()) and self.status not in ["Completed", "Cancelled"]:
			self.status = "Overdue"

		if self.status == "Completed" and not self.completion_date:
			frappe.throw(_("Please select Completion Date for Completed Asset Maintenance Log"))

		if self.status != "Completed" and self.completion_date:
			frappe.throw(_("Please select Maintenance Status as Completed or remove Completion Date"))

	def on_submit(self):
		if self.status not in ['Completed', 'Cancelled']:
			frappe.throw(_("Maintenance Status has to be Cancelled or Completed to Submit"))
		self.update_maintenance_task()

	def update_maintenance_task(self):
		asset_maintenance_doc = frappe.get_doc('Asset Maintenance Task', self.task)
		if self.status == "Completed":
			if asset_maintenance_doc.last_completion_date != self.completion_date:
				# next_due_date = calculate_next_due_date(periodicity = self.periodicity, last_completion_date = self.completion_date)
				asset_maintenance_doc.last_completion_date = self.completion_date
				# asset_maintenance_doc.next_due_date = next_due_date
				asset_maintenance_doc.maintenance_status = "Planned"
				asset_maintenance_doc.save()
		if self.status == "Cancelled":
			asset_maintenance_doc.maintenance_status = "Cancelled"
			asset_maintenance_doc.save()
		asset_maintenance_doc = frappe.get_doc('Asset Maintenance', self.asset_maintenance)
		asset_maintenance_doc.save()

		asset_maintenance_log = frappe.get_value("Asset Maintenance Log", {"asset_maintenance": self.asset_maintenance,
		"task": self.task, "maintenance_status": ('in',['Planned','Overdue'])})
		print(asset_maintenance_log)
		doc = frappe.get_doc('Asset Maintenance Log', asset_maintenance_log)
		doc.maintenance_status = 'Completed'
		doc.completion_date = self.completion_date
		doc.submit()
