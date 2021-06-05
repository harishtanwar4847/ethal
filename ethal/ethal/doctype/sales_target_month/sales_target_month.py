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
			sales_invoice = frappe.get_all('Sales Invoice Item', filters={'item_code': i.item_code}, fields=['total_net_weight'])
			if sales_invoice:
				total_net_weight = 0
				for j in sales_invoice:
					total_net_weight+= j['total_net_weight']
			i.monthmt = total_net_weight	

@frappe.whitelist()
def set_day_and_month_of_date(doc):
	data = json.loads(doc)
	my_date = datetime.strptime(data['date'], '%Y-%m-%d')
	print(my_date)
	year =my_date.strftime('%Y')
	month = my_date.strftime('%B')
	day_month = data['date'].split('-')
	
	return month, year, day_month[1]