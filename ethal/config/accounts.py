from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			'label': _('Custom Doctype'),
			'items': [
				{ 'type': 'doctype', 'name': 'Payment Request and Authorization', 'onboard': 1 }
			]
		},
		{
			'label': _('Custom Reports'),
			'items': [
				{ 'type': 'report', 'name': 'Product Revenue Analysis Report', 'route': 'query-report/Product Revenue Analysis Report' }
			]
		}
	]
