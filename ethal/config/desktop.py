# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"module_name": "Ethal",
			"color": "grey",
			"icon": "octicon octicon-database",
			"type": "module",
			"label": _("Import")
		},
			{
			"module_name": "Accounts",
			"color": "grey",
			"icon": "octicon octicon-file-directory",
			"type": "module",
			"label": _("Accounting")
		}
	]
