# -*- coding: utf-8 -*-
# Copyright (c) 2021, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta, date

class ContractManagement(Document):
	pass

def send_reminder_mail_to_user():
	contract_management = frappe.get_all('Contract Management', {'is_renewable': 'Yes'}, ['responsible_user', 'renewal_remider_days', 'expiry_date', 'name'])
	print(contract_management)
	for i in contract_management:
		get_reminder_date = i['expiry_date'] - timedelta(days=i['renewal_remider_days'])
		today = date.today()
		if today == get_reminder_date:
			frappe.enqueue(method=frappe.sendmail, recipients=i['responsible_user'], sender=None, now=True,
        	subject='Expire Contract', message='Your Contract {0} About To Expire on {1}'.format(i['name'], i['expiry_date']))

