from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			'label': _('Import'),
			'items': [
				{ 
					'type': 'doctype', 'name': 'Import Cost Sheet', 'onboard': 1
				},
					{ 
					'type': 'report', 'name': 'Import Cost Sheet', 'label': _('Import Cost Sheet Report'),  'route': 'query-report/Import Cost Sheet', 'onboard': 1
				},
				{
					'type': 'doctype', 'name': 'Import PO', 'onboard': 1
				}

			]
		},
		{
			'label': _('Factory Reporting'),
			'items': [
				{
					'type': 'doctype', 'name': 'QC', 'onboard': 1	
				},
				{
					'type': 'doctype', 'name': 'Annealing', 'onboard': 1	
				},
				{
					'type': 'doctype', 'name': 'Melting Furnace', 'onboard': 1	
				},
				{
					'type': 'doctype', 'name': 'Vehicle Log', 'onboard': 1
				},
				{
					'type': 'doctype', 'name': 'Incident', 'onboard': 1
				}
			]
		},
		{
			'label': _('Custom Doctypes'),
			'items': [
				{
					'type': 'doctype', 'name': 'Payment Request and Authorization', 'onboard': 1
				},
				{
					'type': 'doctype', 'name': 'EOS Weekly Scorecard', 'onboard': 1
				},
				{
					'type': 'doctype', 'name': 'SOP', 'onboard': 1
				},
				{
					'type': 'doctype', 'name': 'English Outgoing Letter', 'onboard': 1
				},
				{
					'type': 'doctype', 'name': 'Contract Management', 'onboard': 1
				},
				{
					'type': 'doctype', 'name': 'Sales Target Month', 'onboard': 1
				}
			]
		},
		{
			'label': _('Custom Reports'),
			'items': [
				{
					'type': 'doctype', 'label': _('QC Report'), 'name': 'QC', 'route': 'query-report/QC', 'onboard': 1	
				},
				{
					'type': 'doctype', 'label': _('Annealing Report'), 'name': 'QC', 'route': 'query-report/Annealing', 'onboard': 1	
				},
				{
					'type': 'doctype', 'label': _('Melting Furnace Report'), 'name': 'QC', 'route': 'query-report/Melting Furnace', 'onboard': 1	
				},
				{
					'type': 'doctype', 'label': _('EOS Weekly Scorecard Report'), 'name': 'EOS Weekly Scorecard', 'route': 'query-report/EOS Weekly Scorecard', 'onboard': 1
				}
			]
		},
		{
			'label': _('Settings'),
			'items': [
				{
					'type': 'doctype', 'label': _('Admin Settings'), 'name': 'Admin Settings', 'onboard': 1
				}
			]
		},
		{
			'label': _('Weighbridge'),
			'items': [
				{
					'type': 'doctype', 'label': _('Weighbridge'), 'name': 'Weighbridge', 'onboard': 1
				},
				{
					'type': 'doctype', 'label': _('Weighbridge Sync'), 'name': 'Weighbridge Sync', 'onboard': 1
				},
				{
					'type': 'doctype', 'label': _('Weighbridge Material'), 'name': 'Weighbridge Material', 'onboard': 1
				},
			]
		}
	]
