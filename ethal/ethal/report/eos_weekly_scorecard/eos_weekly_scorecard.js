// Copyright (c) 2016, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["EOS Weekly Scorecard"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __('From Date'),
			"fieldtype": "Date",
			"default": frappe.datetime.month_start(),
		},
		{
			"fieldname":"to_date",
			"label": __('To Date'),
			"fieldtype": "Date",
			"default": frappe.datetime.month_end(),
		}
	],
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		for (let i = 0; i < 50; i++) {
			let a = 'week_'+i
			let b = 'target_week_'+i
			let c = 'desired_'+i
			if (column.name == 'Week_'+ i && data[c] == 'More' && data.uom == '%' && ((data[a]/data[b])*100)>= 10.01){
				value = `<div style="color:#6EFF33">${value}</div>`;
			}
			if (column.name == 'Week_'+ i && data[c] == 'More' && data.uom == '%' && ((data[a]/data[b])*100) == 5 || ((data[a]/data[b])*100) == -5){
				value = `<div style="color:#6EFF33">${value}</div>`;
			}
			if (column.name == 'Week_'+ i && data[c] == 'More' && data.uom == '%' && ((data[a]/data[b])*100) == 10 || ((data[a]/data[b])*100) == -10){
				value = `<div style="color:#FFFF33">${value}</div>`;
			}
			if (column.name == 'Week_'+ i && data[c] == 'More' && data.uom == '%' && ((data[a]/data[b])*100) >= -10.01){
				value = `<div style="color:#FF3333">${value}</div>`;
			}
			if (column.name == 'Week_'+ i && data[c] == 'More' && data.uom == '%' && ((data[a]/data[b])*100) >= -10.01){
				value = `<div style="color:#6EFF33">${value}</div>`;
			}
			if (column.name == 'Week_'+ i && data[c] == 'Less' && data.uom == '%' && ((data[a]/data[b])*100) >= 10.01){
				value = `<div style="color:#FF3333">${value}</div>`;
			}
			if (column.name == 'Week_'+ i && data[c] == 'Less' && data.uom == '%' && ((data[a]/data[b])*100) == 10 || ((data[a]/data[b])*100) == -10){
				value = `<div style="color:#FFFF33">${value}</div>`;
			}
			if (column.name == 'Week_'+ i && data[c] == 'Less' && data.uom == '%' && ((data[a]/data[b])*100) == 5 || ((data[a]/data[b])*100) == -5){
				value = `<div style="color:#6EFF33">${value}</div>`;
			}
		  }
		return value;
	},
}
