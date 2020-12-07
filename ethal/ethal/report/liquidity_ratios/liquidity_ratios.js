// Copyright (c) 2016, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Liquidity Ratios"] = {
	"filters": [

	]
};
// frappe.require("assets/erpnext/js/financial_statements.js", function() {
// 	frappe.query_reports["Liquidity Ratios"] = $.extend({}, erpnext.financial_statements);

// 	erpnext.utils.add_dimensions('Liquidity Ratios', 10);

// 	frappe.query_reports["Balance Sheet"]["filters"].push({
// 		"fieldname": "accumulated_values",
// 		"label": __("Accumulated Values"),
// 		"fieldtype": "Check",
// 		"default": 1
// 	});

// 	frappe.query_reports["Balance Sheet"]["filters"].push({
// 		"fieldname": "include_default_book_entries",
// 		"label": __("Include Default Book Entries"),
// 		"fieldtype": "Check",
// 		"default": 1
// 	});
// });