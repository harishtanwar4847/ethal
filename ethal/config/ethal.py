from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			'label': _('Import'),
			'items': [
				{ 'type': 'doctype', 'name': 'Import Cost Sheet', 'onboard': 1 }
			]
		}
	]
