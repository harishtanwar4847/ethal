# -*- coding: utf-8 -*-
# Copyright (c) 2020, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ImportCostSheet(Document):
	pass

@frappe.whitelist()
def get_value(name):
	return frappe.db.get_all('Purchase Invoice Item', {'parent': name}, ['*'])