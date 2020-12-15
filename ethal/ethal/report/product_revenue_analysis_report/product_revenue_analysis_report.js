// Copyright (c) 2016, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */
frappe.require("assets/erpnext/js/sales_trends_filters.js", function() {
	frappe.query_reports["Product Revenue Analysis Report"] = {
		filters: erpnext.get_sales_trends_filters()
	}
});