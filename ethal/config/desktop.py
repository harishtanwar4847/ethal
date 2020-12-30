# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"module_name": "Ethal",
			"color": "grey",
			"icon": "octicon octicon-file-directory",
			"type": "module",
			"force_show": True,
			"label": _("Import")
		}
	]
