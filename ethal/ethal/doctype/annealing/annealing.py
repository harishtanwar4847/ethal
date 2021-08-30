# -*- coding: utf-8 -*-
# Copyright (c) 2021, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json
from datetime import datetime

class Annealing(Document):
	pass

@frappe.whitelist()
def set_day_and_month_of_date(doc):
	data = json.loads(doc)
	my_date = datetime.strptime(data['date'], '%Y-%m-%d')
	day =my_date.strftime('%A')
	month = my_date.strftime('%B')
	day_month = data['date'].split('-')
	
	return day, month, day_month[1]
