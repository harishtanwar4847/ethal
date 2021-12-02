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
	},
	amount: function(frm){
		if (!frm.doc.amount){
			frm.set_value('amount_in_words', '')
		}
		var amount = frm.doc.amount
		var words = new Array();
		words[0] = '';
		words[1] = 'One';
		words[2] = 'Two';
		words[3] = 'Three';
		words[4] = 'Four';
		words[5] = 'Five';
		words[6] = 'Six';
		words[7] = 'Seven';
		words[8] = 'Eight';
		words[9] = 'Nine';
		words[10] = 'Ten';
		words[11] = 'Eleven';
		words[12] = 'Twelve';
		words[13] = 'Thirteen';
		words[14] = 'Fourteen';
		words[15] = 'Fifteen';
		words[16] = 'Sixteen';
		words[17] = 'Seventeen';
		words[18] = 'Eighteen';
		words[19] = 'Nineteen';
		words[20] = 'Twenty';
		words[30] = 'Thirty';
		words[40] = 'Forty';
		words[50] = 'Fifty';
		words[60] = 'Sixty';
		words[70] = 'Seventy';
		words[80] = 'Eighty';
		words[90] = 'Ninety';
		amount = amount.toString();
		var atemp = amount.split(".");
		var number = atemp[0].split(",").join("");
		var n_length = number.length;
		var words_string = "";
		if (n_length <= 9) {
			var n_array = new Array(0, 0, 0, 0, 0, 0, 0, 0, 0);
			var received_n_array = new Array();
			for (var i = 0; i < n_length; i++) {
				received_n_array[i] = number.substr(i, 1);
			}
			for (var i = 9 - n_length, j = 0; i < 9; i++, j++) {
				n_array[i] = received_n_array[j];
			}
			for (var i = 0, j = 1; i < 9; i++, j++) {
				if (i == 0 || i == 2 || i == 4 || i == 7) {
					if (n_array[i] == 1) {
						n_array[j] = 10 + parseInt(n_array[j]);
						n_array[i] = 0;
					}
				}
			}
			var value = "";
			for (var i = 0; i < 9; i++) {
				if (i == 0 || i == 2 || i == 4 || i == 7) {
					value = n_array[i] * 10;
				} else {
					value = n_array[i];
				}
				if (value != 0) {
					words_string += words[value] + " ";
				}
				if ((i == 1 && value != 0) || (i == 0 && value != 0 && n_array[i + 1] == 0)) {
					words_string += "Crores ";
				}
				if ((i == 3 && value != 0) || (i == 2 && value != 0 && n_array[i + 1] == 0)) {
					words_string += "Lakhs ";
				}
				if ((i == 5 && value != 0) || (i == 4 && value != 0 && n_array[i + 1] == 0)) {
					words_string += "Thousand ";
				}
				if (i == 6 && value != 0 && (n_array[i + 1] != 0 && n_array[i + 2] != 0)) {
					words_string += "Hundred and ";
				} else if (i == 6 && value != 0) {
					words_string += "Hundred ";
				}
			}
			words_string = words_string.split("  ").join(" ");
		}
		frm.set_value('amount_in_words', words_string)
	}
//    onload: function(frm){
		
// 	}
});