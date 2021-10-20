// Copyright (c) 2021, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Cash Incentive Bulk', {
	setup: function(frm) {
		frm.set_query("salary_component", function() {
			return {
				filters: {
					"type": "Earning"
				}
			};
		})
		},
		refresh: function(frm) {
			if (frm.doc.docstatus == 0) {
				if(!frm.is_new()) {
					// frm.page.clear_primary_action();
					frm.add_custom_button(__("Get Employees"),
						function() {
							frm.events.get_employee_details(frm);
						}
					).toggleClass('btn-primary', !(frm.doc.employee_details || []).length);
				}
				// if ((frm.doc.employee_details || []).length) {
				// 	frm.page.set_primary_action(__('Create Salary Slips'), () => {
				// 		frm.save('Submit').then(()=>{
				// 			frm.page.clear_primary_action();
				// 			frm.refresh();
				// 			frm.events.refresh(frm);
				// 		});
				// 	});
				// }
			}
	
			// if (frm.doc.docstatus == 1) {
			// 	if (frm.custom_buttons) frm.clear_custom_buttons();
			// 	frm.events.add_context_buttons(frm);
			// }
		},
	
		get_employee_details: function (frm) {
			return frappe.call({
				doc: frm.doc,
				method: 'fill_employee_details',
				callback: function(r) {
					console.log(r)
					if (r.docs[0].employee_details){
						frm.save();
						frm.refresh();
					}
				}
			})
		},
});
