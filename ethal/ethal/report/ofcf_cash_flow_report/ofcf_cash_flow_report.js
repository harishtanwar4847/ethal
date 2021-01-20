// Copyright (c) 2016, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["OFCF CASH FLOW Report"] = {
	"filters": [
		{
			"fieldname":"year",
			"label": __("Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"default": frappe.defaults.get_user_default("fiscal_year"),
			"reqd": 1,
			"width": "60px"
		}
	]
};
