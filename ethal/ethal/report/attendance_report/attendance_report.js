// Copyright (c) 2016, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Attendance Report"] = {
	"filters": [
		{
			'label': __('From Date'),
			'fieldname': 'from_date',
			'fieldtype': 'Date',
			'default': frappe.datetime.get_today()
		},
		{
			'label': __('To Date'),
			'fieldname': 'to_date',
			'fieldtype': 'Date',
			'default': frappe.datetime.get_today()
		},
		{
			'label': __('Status'),
			'fieldname': 'status',
			'fieldtype': 'Select',
			'options': ['', __('Present'), __('Absent'), __('On Leave'), __('Half Day')],
			'default': 'Present'
		},
		{
			'label': __('Department'),
			'fieldname': 'department',
			'fieldtype': 'Link',
			'options': 'Department'
		},
		{
			'label': __('Working Area'),
			'fieldname': 'working_area',
			'fieldtype': 'Link',
			'options': 'Working Area'
		},
		{
			'label': __('Shift'),
			'fieldname': 'shift',
			'fieldtype': 'Link',
			'options': 'Shift Type'
		}
	]
};
