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

		var obj_lst = Object.keys(data)

	    const array1 = obj_lst.filter((str) => str.startsWith('actual'));
		const array2 = obj_lst.filter((str) => str.startsWith('target'));
		const array3 = obj_lst.filter((str) => str.startsWith('desired'));
		const zip = (...arr) => {
			const zipped = [];
			arr.forEach((element, ind) => {
			   element.forEach((el, index) => {
				  if(!zipped[index]){
					 zipped[index] = [];
				  };
				  if(!zipped[index][ind]){
					 zipped[index][ind] = [];
				  }
				  zipped[index][ind] = el || '';
			   })
			});
			return zipped;
		 };
		 var final_array = zip(array1, array2, array3)

		 for (let i = 0; i < final_array.length; i++) {
			for (let j = 0; j < final_array[i].length; j++) {
			    let a = final_array[i][0]
			    let b = final_array[i][1]
			    let c = final_array[i][2]
			    
			    if (column.fieldname == a && data[c] == 'More' && ((data[a]/data[b])*100)>= 10.01){
					value = `<div style="color:#6EFF33">${value}</div>`;
			    }
			    if (column.fieldname == a && data[c] == 'More' && ((data[a]/data[b])*100) == 5 || ((data[a]/data[b])*100) == -5){
					value = `<div style="color:#6EFF33">${value}</div>`;
				}
			    if (column.fieldname == a && data[c] == 'More' && ((data[a]/data[b])*100) == 10 || ((data[a]/data[b])*100) == -10){
					value = `<div style="color:#FFFF33">${value}</div>`;
				}
				if (column.fieldname == a && data[c] == 'More' && ((data[a]/data[b])*100) >= -10.01){
					value = `<div style="color:#FF3333">${value}</div>`;
				}
				if (column.fieldname == a && data[c] == 'Less' && ((data[a]/data[b])*100) >= 10.01){
					value = `<div style="color:#FF3333">${value}</div>`;
				}
				if (column.fieldname == a && data[c] == 'Less' && ((data[a]/data[b])*100) >= -10.01){
					value = `<div style="color:#6EFF33">${value}</div>`;
				}
				if (column.fieldname == a && data[c] == 'Less' && ((data[a]/data[b])*100) == 10 || ((data[a]/data[b])*100) == -10){
					value = `<div style="color:#FFFF33">${value}</div>`;
				}
				if (column.fieldname == a && data[c] == 'Less' && ((data[a]/data[b])*100) == 5 || ((data[a]/data[b])*100) == -5){
					value = `<div style="color:#6EFF33">${value}</div>`;
				}
			}
		 }
		return value;
    },

}
