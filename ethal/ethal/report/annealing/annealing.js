// Copyright (c) 2016, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Annealing"] = {
	"filters": [
		{
			"fieldname":"annealing",
			"label": __('Annealing'),
			"fieldtype": "Link",
			"options": "Annealing",
			// "on_change": function(query_report) {
			// 	var name = query_report.get_values().annealing
			// 	console.log(name)
			// 	frappe.db.get_list('Annealing', {
			// 		fields: ['date', 'day', 'month'],
			// 		filters: {
			// 			name: name
			// 		}
			// 	}).then(records => {
			// 		console.log(records[0]);
			// 		frappe.query_report.set_filter_value('date', records[0].date)
			// 		frappe.query_report.set_filter_value('day', records[0].day)
			// 		frappe.query_report.set_filter_value('month', records[0].month)
			// 	})
			// }		
		},
		{
			"fieldname":"from_date",
			"label": __('From Date'),
			"fieldtype": "Date"
		},
		{
			"fieldname":"to_date",
			"label": __('To Date'),
			"fieldtype": "Date"
		},
		// {
		// 	"fieldname":"day",
		// 	"label": __('Day'),
		// 	"fieldtype": "Data",
		// 	"read_only": 1
		// },
		// {
		// 	"fieldname":"month",
		// 	"label": __('Month'),
		// 	"fieldtype": "Data",
		// 	"read_only": 1
		// }
	]
};
