// Copyright (c) 2016, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Import Cost Sheet"] = {
	"filters": [
		{
			"fieldname":"import_cost_sheet",
			"label": __('Import Cost Sheet'),
			"fieldtype": "Link",
			"options": "Import Cost Sheet",
			"on_change": function(query_report) {
				var name = query_report.get_values().import_cost_sheet
				console.log(name)
				frappe.db.get_list('Import Cost Sheet', {
					fields: ['purchase_order_no', 'supplier_name', 'invoice_value', 'bl', 'grn'],
					filters: {
						name: name
					}
				}).then(records => {
					console.log(records[0]);
					frappe.query_report.set_filter_value('grn', records[0].grn)
					frappe.query_report.set_filter_value('for_purchase_order_no', records[0].purchase_order_no)
					frappe.query_report.set_filter_value('supplier_name', records[0].supplier_name)
					frappe.query_report.set_filter_value('invoice_value', records[0].invoice_value)
					frappe.query_report.set_filter_value('bl', records[0].bl)
				})
			}		
		},
		{
			"fieldname":"for_purchase_order_no",
			"label": __('For Purchase Order No.'),
			"fieldtype": "Data",
			"read_only": 1
		},
		{
			"fieldname":"supplier_name",
			"label": __('Supplier Name'),
			"fieldtype": "Data",
			"read_only": 1
		},
		{
			"fieldname":"invoice_value",
			"label": __('Invoice Value'),
			"fieldtype": "Currency",
			"read_only": 1
		},
		{
			"fieldname":"bl",
			"label": __('BL'),
			"fieldtype": "Data",
			"read_only": 1
		},
		{
			"fieldname":"grn",
			"label": __('GRN'),
			"fieldtype": "Link",
			"options": "Purchase Receipt",
			"read_only": 1
		}
	]
};
