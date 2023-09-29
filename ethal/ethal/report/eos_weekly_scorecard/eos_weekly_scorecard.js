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
		const array2 = obj_lst.filter((str) => str.startsWith('week'));
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
			    let actual = final_array[i][0]
			    let week = final_array[i][1]
			    let desired = final_array[i][2]
			    
			    const percentageDifference = ((data[actual] - data[week]) / data[week]) * 100;
				if (column.fieldname == actual) {
					if (data[desired] === "More") {
						if (percentageDifference <= 5 && percentageDifference >= -5) {
						value = `<div style="background-color:#6EFF33">${value}</div>`; // Within +/- 5%, GREEN
						} else if (percentageDifference <= -5.01) {
						value = `<div style="background-color:#FF3333">${value}</div>`; // Less than -5.01%, RED
						} else if (percentageDifference >= 5.01) {
						value = `<div style="background-color:#6EFF33">${value}</div>`; // More than 5.01%, GREEN
						}
					} else if (data[desired] === "Less") {
						if (percentageDifference <= 5 && percentageDifference >= -5) {
						value = `<div style="background-color:#6EFF33">${value}</div>`; // Within +/- 5%, GREEN
						} else if (percentageDifference <= -5.01) {
						value = `<div style="background-color:#6EFF33">${value}</div>`; // Less than -5.01%, GREEN
						} else if (percentageDifference >= 5.01) {
						value = `<div style="background-color:#FF3333">${value}</div>`; // More than 5.01%, RED
						}
					}			
				} 
			}
		}

	return value;
},

}
