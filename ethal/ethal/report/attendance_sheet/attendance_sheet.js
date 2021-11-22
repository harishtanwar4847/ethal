// Copyright (c) 2016, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Attendance Sheet"] = {
	"filters": [
		{
			"label": __("Department"),
			"fieldname": "department",
			"fieldtype": "Link",
			"options": "Department"
		},
		{
			"label": __("Working Area"),
			"fieldname": "working_area",
			"fieldtype": "Link",
			"options": "Working Area"
		},
		{
			"label": __("Date"),
			"fieldname": "date",
			"fieldtype": "Date",
			'default': frappe.datetime.get_today()
		}	
	]
};
