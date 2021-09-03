# -*- coding: utf-8 -*-
# Copyright (c) 2021, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document

class Weighbridge(Document):
	def before_insert(self):
		self.set_weighbridge_movement_type()

	def set_weighbridge_movement_type(self):
		if self.wb1 > self.wb2:
			self.movement_type = 'Inward'
		else:
			self.movement_type = 'Outward'	