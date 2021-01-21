// Copyright (c) 2020, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Import Cost Sheet', {
	refresh: function(frm) {

	},
	setup: function(frm){
		if (frm.doc.import_cost_sheet_items == undefined) {
		var l = ['Sea Fright (ETB)', 'Inland Fright (ETB)', 'Insurance (ETB)', 'Import Customs Duty (ETB)', 'Other (ETB)', 'Bank charge (ETB)', 'Storage (ETB)', 'Port handling charge (ETB)', 'Transit and clearing (ETB)', 'Loading & unloading (ETB)', 'Inland transport (ETB)', 'Miscellaneous (ETB)']
		
		for (var i = 0; i < l.length; i++) {
			var childTable = cur_frm.add_child("import_cost_sheet_items");
			console.log(i)
			childTable.items = l[i]
		}
		cur_frm.refresh_fields("import_cost_sheet_items");
		}
	},
	purchase_invoice: function(frm){
	
		frappe.call({
			method:"ethal.ethal.doctype.import_cost_sheet.import_cost_sheet.get_value",
			args: {
			name: frm.doc.purchase_invoice
			}
		})
		.success(success => {
		var total_amount = 0
		for (var i=0; i<success.message.length; i++){
			total_amount += success.message[i].amount
		}
		for (var i=0; i<success.message.length; i++){
			let row = frm.add_child('import_cost_sheet_details')
			row.parameters= success.message[i].item_code
			// row.amount = success.message[i].amount
			
			// 	console.log(success.message[i])
			// 	switch(success.message[i].item_name) {
			// 		case "Sea Fright":
			// 			row.sea_fright_etb = success.message[i].amount
			// 			break;
			// 		case "Inland Fright":
			// 			row.inland_fright_etb = success.message[i].amount
			// 		    break;
			// 		case "Insurance":
			// 			row.insurance_etb = success.message[i].amount
			// 		  	break;
			// 		case "Import Customs Duty":
			// 			row.import_customs_duty_etb = success.message[i].amount
			// 			break;
			// 		case "Other":
			// 			row.other_etb = success.message[i].amount
			// 		  	break;
			// 		case "Bank charge":
			// 			row.bank_charge_etb = success.message[i].amount
			// 		  	break;
			// 		case "Storage":
			// 			row.storage_etb = success.message[i].amount
			// 			break;
			// 		case "Port handling charge":
			// 			row.port_handling_charge_etb = success.message[i].amount
			// 		  	break;
			// 		case "Transit and clearing":
			// 			row.transit_and_clearing_etb = success.message[i].amount
			// 		  	break;
			// 		case "Loading and unloading":
			// 			row.loading_and_unloading_etb = success.message[i].amount
			// 			break;
			// 		case "Inland transport":
			// 			row.inland_transport_etb = success.message[i].amount
			// 		  	break;
			// 		case "Miscellaneous":
			// 			row.miscellaneous_etb = success.message[i].amount
			// 		  	break;
			// 	  }
			// row.amount = total_amount
	    }
		  frm.refresh_field('import_cost_sheet_details');
		})
	},
	
	// amount: function(frm, cdt, cdn){
	// 	console.log('ja na be')
	// }
});

frappe.ui.form.on('Import Cost Sheet Details', {
	// import_cost_sheet_details_add: function(frm){
	// 	console.log('hello')
	// 	var total_sales = 0;
	// 	$.each(frm.doc.import_cost_sheet_details || [], function(i, d) {
	// 		console.log('hello', d)
	// 	total_sales += flt(d.amount);
	// 	});
	// 	frm.set_value("net_total", total_sales);
	// 	frm.set_df_property('net_total', 'read_only', 1)
	// },
	// amount: function(frm){
	// 	// console.log(amount)
	// 	console.log('ja na be')
	// 	console.log(frm.doc.exchange_rate )
	// 	var a = frm.doc.exchange_rate * frm.doc.amount
	// 	frm.doc.amount__etb_ = a
	// 	frm.refresh_field("import_cost_sheet_details");
	// }
});