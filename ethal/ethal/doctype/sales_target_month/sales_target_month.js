// Copyright (c) 2021, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Target Month', {
	date: function(frm) {
		if (frm.doc.date) {
			frappe.call({
				'method': 'ethal.ethal.doctype.sales_target_month.sales_target_month.set_day_and_month_of_date',
				'args': {
					'doc': frm.doc
				}
			})
			.success(success => {
				console.log(success)
				frm.set_value('month', success.message[0])
				frm.set_value('year', success.message[1])
				frm.set_value('month_year', success.message[2])
			})
		}	
	}
});
