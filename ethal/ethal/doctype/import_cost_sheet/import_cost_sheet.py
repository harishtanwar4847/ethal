# -*- coding: utf-8 -*-
# Copyright (c) 2020, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ImportCostSheet(Document):
	def after_insert(self):
		print("ja na be", self.name)
		items = frappe.db.get_all('Import Cost Sheet Items', {'parent': self.name}, ['items', 'amount'])
		for i in items:
			if i['items'] == 'Sea Fright (ETB)':
				print(i['amount'])
				a = frappe.db.get_all('Import Cost Sheet Details', {'parent': self.name}, ['idx'], as_list=True)
				print(a)
		frappe.throw('ja na be')


@frappe.whitelist()
def get_value(name):
	return frappe.db.get_all('Purchase Invoice Item', {'parent': name}, ['*'])