# -*- coding: utf-8 -*-
# Copyright (c) 2021, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class EOSWeeklyScorecard(Document):
	pass

@frappe.whitelist()
def get_previous_record(doc):
	get_parent = frappe.db.get_all('EOS Weekly Scorecard', ['name'], order_by='name desc', page_length=1)
	if get_parent:
		get_previous_record = frappe.db.get_all('EOS Weekly Scorecard Details', {'parent': get_parent[0]['name']}, ['*'], order_by='idx asc')
		return get_previous_record
