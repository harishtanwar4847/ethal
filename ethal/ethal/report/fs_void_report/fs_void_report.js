// Copyright (c) 2016, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["FS Void Report"] = {
	"filters": [
		{
			"label": "From No",
			"fieldtype": 'Int',
			"fieldname": "from_no"
		},
		{
			"label": "To No",
			"fieldtype": "Int",
			"fieldname": 'to_no'
		}

	]
};
