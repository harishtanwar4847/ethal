// Copyright (c) 2020, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payment Request and Authorization', {
	// refresh: function(frm) {

	// }
	on_submit: function(frm){
		if(frm.doc.docstatus == 1){
		  frappe.call({
			  method: "ethal.utils.set_approver_name",
			  args: {
				  data: frm.doc
			  }
		  })
		  .success(success =>{
		  })
	   }
   }
});
