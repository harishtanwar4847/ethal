// Copyright (c) 2020, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Warning Letter', {
	// refresh: function(frm) {

	// }
	employee: function(frm) {
		frappe.call({
			"method": "ethal.ethal.doctype.warning_letter.warning_letter.set_warning",
			"args": {
				'employee': frm.doc.employee
			},
			callback: function(r){
				console.log(r.message)
				if (r.message == 1) {
				frm.doc.warning_number = 1
				frm.refresh_field('warning_number')
				}
				else{
					frm.doc.warning_number = r.message
				frm.refresh_field('warning_number')
				}
			}
		})
	},
	after_save: function(frm){
		frappe.call({
			"method": "ethal.ethal.doctype.warning_letter.warning_letter.set_warning_in_employee",
			"args": {
				'employee': frm.doc.employee,
				'name': frm.doc.name
			},
			callback: function(r){
				console.log(r.message)
		
				
			}
		})
		
	}
});
