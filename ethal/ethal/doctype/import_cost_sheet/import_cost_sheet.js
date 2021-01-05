// Copyright (c) 2020, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Import Cost Sheet', {
	// refresh: function(frm) {

	// }
	// setup: function(frm){
	// 	var l = ['Invoice Value', 'Sea Fright (ETB)', 'Inland Fright (ETB)', 'Insurance (ETB)', 'Import Customs Duty (ETB)', 'Other (ETB)', 'Bank charge (ETB)', 'Storage (ETB)', 'Port handling charge (ETB)', 'Transit and clearing (ETB)', 'Loading & unloading (ETB)', 'Inland transport (ETB)', 'Miscellaneous (ETB)']
		
	// 	for (var i = 0; i < l.length; i++) {
	// 		var childTable = cur_frm.add_child("import_cost_sheet_details");
	// 		console.log(i)
	// 		childTable.parameters = l[i]
	// 	}
	// 	cur_frm.refresh_fields("import_cost_sheet_details");
	// },
		
});

frappe.ui.form.on('Import Cost Sheet Details', {
	amount: function(frm){
		var total_sales = 0;
		$.each(frm.doc.import_cost_sheet_details || [], function(i, d) {
			console.log('hello', d)
		total_sales += flt(d.amount);
		});
		frm.set_value("net_total", total_sales);
		frm.set_df_property('net_total', 'read_only', 1)
	},
	purchase_invoice: function(frm){
		$.each(frm.doc.import_cost_sheet_details || [], function(i, d) {
			console.log('hello', d.purchase_invoice)
		console.log('ja na be')
		frappe.call({
			method:"ethal.ethal.doctype.import_cost_sheet.import_cost_sheet.get_value",
			args: {
			name: d.purchase_invoice
			}
		})
		.success(success => {

			for (var i=0; i<success.message.length; i++){
			
			let row = frm.add_child('import_cost_sheet_details')
			row.parameters= success.message[i].item_code
			row.purchase_invoice = success.message[i].parent
			row.amount = success.message[i].amount
		  }
		  frm.refresh_field('import_cost_sheet_details');
		})
	});
	}
});