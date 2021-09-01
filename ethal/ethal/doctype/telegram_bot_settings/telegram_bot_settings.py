# Copyright (c) 2021, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import requests
from frappe.model.document import Document

class TelegramBotSettings(Document):
	def send_telegram_message(self, message, group):
		try:
			if not self.bot_api_token:
				return
			else:
				group_id = None
				if group == 'Sales':
					group_id = self.sales_group_id
				elif group == 'Purchase':
					group_id = self.purchase_group_id
				elif group == 'Stock':
					group_id = self.stock_group_id

				self.hit_telegram_send_message_api(group_id, message)	

		except requests.exceptions.RequestException:
			frappe.log_error(title='Telegram Bot API Hit error')
					

	def hit_telegram_send_message_api(self, group_id, message):
		response = requests.get('https://api.telegram.org/{}/sendMessage?chat_id={}&text={}'.format(self.bot_api_token, group_id, message))			
