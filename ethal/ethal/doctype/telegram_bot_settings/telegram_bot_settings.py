# Copyright (c) 2021, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import requests
from frappe.model.document import Document

class TelegramBotSettings(Document):
	def send_telegram_message(self, message, group):
		if self.bot_api_token:
			if group == 'Sales' and self.sales_group_id:
				get_request(self.bot_api_token, self.sales_group_id, message)
			if group == 'Purchase':
				get_request(self.bot_api_token, self.purchase_group_id, message)	
			if group == 'Stock':
				get_request(self.bot_api_token, self.stock_group_id, message)		

def get_request(token, group_id, message):
	response = requests.get('https://api.telegram.org/{}/sendMessage?chat_id={}&text={}'.format(token, group_id, message))			
