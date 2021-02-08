from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			'label': _('Other Reports'),
			'items': [
				{ 'type': 'report', 'name': 'Customer Spread Report', 'route': 'query-report/Customer Spread Report' }
			]
		}
	]
