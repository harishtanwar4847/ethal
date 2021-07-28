from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			'label': _('Other Reports'),
			'items': [
				{ 
					'type': 'report', 'name': 'Customer Spread Report', 'onboard': 1, 'route': 'query-report/Customer Spread Report' 
				},
				{
					'type': 'report', 'name': 'Customer Ledger With Item Name', 'route': 'query-report/Customer Ledger With Item Name' 
				}
			]
		}
	]
