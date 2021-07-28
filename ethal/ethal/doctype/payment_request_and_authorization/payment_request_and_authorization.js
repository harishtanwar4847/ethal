// Copyright (c) 2020, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payment Request and Authorization', {
	refresh: function(frm) {
		if(frm.doc.workflow_state == 'Approved'){
			frm.add_custom_button('Create Payment Entry', () => {
				
				frappe.call({
					method: "ethal.ethal.doctype.payment_request_and_authorization.payment_request_and_authorization.create_payment_entry",
					args: {
						doc: frm.doc
					},
				callback: function(r) {
					console.log(r)
					var doclist = frappe.model.sync(r.message);
				
					frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
					}
				})
			})
		}
		if(frm.doc.workflow_state == 'Sent For Approval' && !frm.doc.checked_person){
			frappe.call({
				method: "ethal.ethal.doctype.payment_request_and_authorization.payment_request_and_authorization.set_approver_name",
				args: {
					data: frm.doc
				}
			})
			.success(success =>{
				console.log(success)
			})
		} 
		if(frm.doc.workflow_state == 'Approved' && !frm.doc.checked_person){
			frappe.call({
				method: "ethal.ethal.doctype.payment_request_and_authorization.payment_request_and_authorization.set_approver_name",
				args: {
					data: frm.doc
				}
			})
			.success(success =>{
				console.log(success)
			})
		} 

	},
	setup: function(frm){
		frm.set_query("party_type", function() {
			return{
				filters: {
					"name": ["in", Object.keys(frappe.boot.party_account_types)],
				}
			}
		});
	},
	party_type: function(frm) {

		let party_types = Object.keys(frappe.boot.party_account_types);
		if(frm.doc.party_type && !party_types.includes(frm.doc.party_type)){
			frm.set_value("party_type", "");
			frappe.throw(__("Party can only be one of "+ party_types.join(", ")));
		}
	},
	party: function(frm) {
		if (!frm.doc.party) {
			frm.set_value('payee_name', '')
		}
	}
//    onload: function(frm){
		
// 	}
});