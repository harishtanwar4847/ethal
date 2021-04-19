# -*- coding: utf-8 -*-
# Copyright (c) 2021, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class EOSWeeklyScorecard(Document):
	def validate(self):
		for idx, val in enumerate(self.eos_details):
			if val.parameter == 'Achieved':
				a= val.idx - 2
				previous_values = self.eos_details[a].actual / self.eos_details[a].target if self.eos_details[a].actual and self.eos_details[a].target else 0
				val.actual = previous_values

@frappe.whitelist()
def get_previous_record(doc):
	get_parent = frappe.db.get_all('EOS Weekly Scorecard', ['name'], order_by='name desc', page_length=1)
	if get_parent:
		get_previous_record = frappe.db.get_all('EOS Weekly Scorecard Details', {'parent': get_parent[0]['name']}, ['*'], order_by='idx asc')
		return get_previous_record










