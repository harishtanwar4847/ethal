// Copyright (c) 2021, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gate Pass', {
	// refresh: function(frm) {

	// }
	delivery_memo_no: function(frm){
		if (frm.doc.delivery_memo_no && frm.doc.gate_pass_type == 'Sale'){
			frappe.model.get_value('Delivery Note', {'name': frm.doc.delivery_memo_no}, ['posting_date', 'customer'],
			function(d) {
				frm.set_value('delivery_memo_date', d.posting_date)
				frm.set_value('material_sent_to', d.customer)
			})
			cur_frm.clear_table("material");
			frappe.call({
				method: "ethal.ethal.doctype.gate_pass.gate_pass.get_delivery_note_items",
				args: {
					name: frm.doc.delivery_memo_no
				},
				callback: function(r){
				   let op = r.message
					var childTable = cur_frm.add_child("material");
					childTable.item=op['item_code']
					childTable.item_name=op['item_name']
					childTable.uom=op['uom']
					childTable.qty=op['qty']
					cur_frm.refresh_fields("material");
					frm.set_value('vat_invoice_no', op['against_sales_order'])
				}
			})
		}
	},
	before_save: function(frm){
		if (frm.doc.vat_invoice_no && frm.doc.gate_pass_type == 'Sale'){
			frappe.model.get_value('Sales Invoice', {'name': frm.doc.vat_invoice_no}, 'posting_date',
			function(d) {
				console.log(d)
				frm.set_value('vat_invoice_date', d.posting_date)
			})
		}
	}
});
