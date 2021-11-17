// Copyright (c) 2016, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Attendance Summary"] = {
	"filters": [
		{
			'label': __('Date'),
			'fieldname': 'date',
			'fieldtype': 'Date',
			'default': frappe.datetime.get_today()
		}
	]
};
