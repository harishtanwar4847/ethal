# -*- coding: utf-8 -*-
# Copyright (c) 2021, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime
from frappe.model.document import Document

class Annealing(Document):
	def after_insert(self):
		if self.date:
			my_date = datetime.strptime(self.date, '%Y-%m-%d')
			day =my_date.strftime('%A')
			month = my_date.strftime('%B')
			self.day = day
			self.month = month

	def before_save(self):
		if self.date:
			print(self.date)
			my_date = datetime.strptime(self.date, '%Y-%m-%d')
			day =my_date.strftime('%A')
			month = my_date.strftime('%B')
			self.day = day
			self.month = month	