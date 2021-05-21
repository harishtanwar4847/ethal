// Copyright (c) 2020, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Import Cost Sheet', {
	refresh: function(frm) {
		frm.set_query('grn', () => {
			return {
				filters: {
					docstatus: 1
				}
			}
		})
		frm.set_query('purchase_invoice', () => {
			return {
				filters: {
					docstatus: 1
				}
			}
		})
		frm.fields_dict['import_cost_sheet_items'].grid.get_field("purchase_invoice").get_query = function(doc, cdt, cdn) {
	        return{
	            filters: {
					docstatus: 1
				}
	        }
	    }
		if (frm.doc.import_cost_sheet_items == undefined) {
			var l = ['Sea Fright (ETB)', 'Inland Fright (ETB)', 'Insurance (ETB)', 'Import Customs Duty (ETB)', 'Other (ETB)', 'Bank charge (ETB)', 'Storage (ETB)', 'Port handling Charge (ETB)', 'Transit and Clearing (ETB)', 'Loading & Unloading (ETB)', 'Inland Transport (ETB)', 'Miscellaneous (ETB)']
			
			for (var i = 0; i < l.length; i++) {
				var childTable = cur_frm.add_child("import_cost_sheet_items");
				console.log(i)
				childTable.items = l[i]
			}
			cur_frm.refresh_fields("import_cost_sheet_items");
			}
		},
	grn: function(frm){
		if (frm.doc.grn){
			frm.clear_table("import_cost_sheet_details"); 
			frm.refresh_field('import_cost_sheet_details');
			frappe.call({
				method:"ethal.ethal.doctype.import_cost_sheet.import_cost_sheet.get_value",
				args: {
				name: frm.doc.grn
				}
			})
			.success(success => {
			var total_amount = 0
			for (var i=0; i<success.message.length; i++){
				total_amount += success.message[i].amount
			}
			for (var i=0; i<success.message.length; i++){
				let row = frm.add_child('import_cost_sheet_details')
				row.item_code= success.message[i].item_code
				row.qty = success.message[i].qty
			}
			frm.refresh_field('import_cost_sheet_details');
			})
		}
	},
	before_save: function(frm) {
		var total_sales = 0;
		$.each(frm.doc.import_cost_sheet_items || [], function(i, d) {
			total_sales += flt(d.amount);
		});
		frm.set_value("net_total", total_sales);
	}
});

frappe.ui.form.on('Import Cost Sheet Items', {
	import_cost_sheet_items: function(frm){
		
		// frm.set_df_property('net_total', 'read_only', 1)
	},
	// amount: function(frm){
	// 	// console.log(amount)
	// 	console.log('ja na be')
	// 	console.log(frm.doc.exchange_rate )
	// 	var a = frm.doc.exchange_rate * frm.doc.amount
	// 	frm.doc.amount__etb_ = a
	// 	frm.refresh_field("import_cost_sheet_details");
	// }
});