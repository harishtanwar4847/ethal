# -*- coding: utf-8 -*-
# Copyright (c) 2021, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime
import json

class QC(Document):
	def after_insert(self):
		print("qc items",self.qc_items)
		if self.date:
			my_date = datetime.strptime(self.date, '%Y-%m-%d')
			day =my_date.strftime('%A')
			month = my_date.strftime('%B')
			self.day = day
			self.month = month
		for i in self.qc_items:
			print(i)
			i.total_rejection = i.rejection_ash+i.rejection_blister+i.rejection_rolling+i.rejection_others
			i.melting_rejection = i.rejection_ash+i.rejection_blister
			i.total_circle_received = i.ok_circle_received+i.total_rejection
			i.save(ignore_permissions=True)

	def before_save(self):
		print(self.qc_items)
		if self.date:
			my_date = datetime.strptime(self.date, '%Y-%m-%d')
			day =my_date.strftime('%A')
			month = my_date.strftime('%B')
			self.day = day
			self.month = month
		for i in self.qc_items:
			print(i)
			i.total_rejection = i.rejection_ash+i.rejection_blister+i.rejection_rolling+i.rejection_others
			i.melting_rejection = i.rejection_ash+i.rejection_blister
			i.total_circle_received = i.ok_circle_received+i.total_rejection		

@frappe.whitelist()
def set_day_and_month_of_date(doc):
	data = json.loads(doc)
	my_date = datetime.strptime(data['date'], '%Y-%m-%d')
	day =my_date.strftime('%A')
	month = my_date.strftime('%B')
	return day, month