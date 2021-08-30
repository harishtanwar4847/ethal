// Copyright (c) 2021, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Melting Furnace', {
	date: function(frm) {
		if (frm.doc.date) {
			console.log('ja na')
			frappe.call({
				'method': 'ethal.ethal.doctype.melting_furnace.melting_furnace.set_day_and_month_of_date',
				'args': {
					'doc': frm.doc
				}
			})
			.success(success => {
				console.log(success)
				frm.set_value('day', success.message[0])
				frm.set_value('month', success.message[1])
			})
		}	
	}
});
