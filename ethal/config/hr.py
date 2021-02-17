from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			'label': _('Payroll'),
			'items': [
				{ 'type': 'doctype', 'name': 'Employee Incentive Bulk', "onboard": 1 }
			]
		}
	]
