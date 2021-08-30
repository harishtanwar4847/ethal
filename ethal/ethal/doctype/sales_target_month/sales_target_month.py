# -*- coding: utf-8 -*-
# Copyright (c) 2021, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from datetime import datetime
from frappe.model.document import Document

class SalesTargetMonth(Document):
	def before_save(self):
		for i in self.sales_target_month_details:
			i.monthisuzu = i.week1isuzu + i.week2isuzu + i.week3isuzu + i.week4isuzu
			if i.item_code:
				i.items_per_isuzu = frappe.db.get_value('Item', i.item_code, 'uom_per_isuzu')
				i.weight_per_unit = frappe.db.get_value('Item', i.item_code, 'weight_per_unit')
			i.monthmt = (i.monthisuzu * i.items_per_isuzu * i.weight_per_unit ) / 1000	

@frappe.whitelist()
def set_day_and_month_of_date(doc):
	data = json.loads(doc)
	my_date = datetime.strptime(data['date'], '%Y-%m-%d')
	print(my_date)
	year =my_date.strftime('%Y')
	month = my_date.strftime('%B')
	day_month = data['date'].split('-')
	
	return month, year, day_month[1]