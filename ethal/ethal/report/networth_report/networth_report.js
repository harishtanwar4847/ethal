// Copyright (c) 2016, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

// frappe.query_reports["Networth Report"] = {
// 	"filters": [

// 	]
// };

frappe.require("assets/erpnext/js/financial_statements.js", function() {
	frappe.query_reports["Networth Report"] = $.extend({}, erpnext.financial_statements);

	erpnext.utils.add_dimensions('Networth Report', 10);

	frappe.query_reports["Networth Report"]["filters"].push({
		"fieldname": "accumulated_values",
		"label": __("Accumulated Values"),
		"fieldtype": "Check",
		"default": 1
	});

	frappe.query_reports["Networth Report"]["filters"].push({
		"fieldname": "include_default_book_entries",
		"label": __("Include Default Book Entries"),
		"fieldtype": "Check",
		"default": 1
	});

	frappe.query_reports["Networth Report"]["filters"].push({
		"fieldname": "account",
		"label": __("Account"),
		"fieldtype": "MultiSelectList",
		get_data: function(txt) {
			return frappe.db.get_link_options('Account', txt);
		}
	});
});