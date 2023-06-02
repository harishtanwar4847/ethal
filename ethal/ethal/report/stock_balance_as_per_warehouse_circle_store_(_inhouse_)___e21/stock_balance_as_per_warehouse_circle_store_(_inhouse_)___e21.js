// Copyright (c) 2016, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["STOCK BALANCE AS PER WAREHOUSE CIRCLE STORE ( INHOUSE ) - E21"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "60px"
		},
		{
            "fieldname":"company",
            "label":("Company"),
            "fieldtype":"Link",
            "options":"Company",
            "default":"Ethal 2021"
        },
		{
            "fieldname":"warehouse",
            "label":("Warehouse"),
            "fieldtype":"Link",
            "options":"Warehouse",
            "default":"CIRCLE STORE ( INHOUSE ) - E21"
        }

	]
};
