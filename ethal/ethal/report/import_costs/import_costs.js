// Copyright (c) 2016, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Import Costs"] = {
	"filters": [
		{
			"fieldname":"account",
			"label": __('Account'),
			"fieldtype": "Link",
			"options": "Account",
		}
	]
};
