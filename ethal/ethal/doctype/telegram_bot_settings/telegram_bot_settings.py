# Copyright (c) 2021, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import requests
from frappe.model.document import Document
import urllib

class TelegramBotSettings(Document):
	def send_telegram_message(self, message, group):
		group_id = None
		if not self.bot_api_token:
			return
		if group == 'Sales':
			group_id = self.sales_group_id
		elif group == 'Purchase':
			group_id = self.purchase_group_id
		elif group == 'Stock':
			group_id = self.stock_group_id
		elif group_id == 'Accounts':
			group_id = self.accounts_group_id

		self.hit_telegram_send_message_api(group_id, message)			

	def hit_telegram_send_message_api(self, group_id, message):
		try:
			encode_message = urllib.parse.quote(message)
			response = requests.get('https://api.telegram.org/{}/sendMessage?chat_id={}&text={}'.format(self.bot_api_token, group_id, encode_message))	
		except requests.exceptions.RequestException:
			frappe.log_error(title='Telegram Bot API Hit error')	
