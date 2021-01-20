// Copyright (c) 2020, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Interview Configuration', {
	after_save: function(frm){
        frappe.call({
            "method": "ethal.ethal.doctype.interview_configuration.interview_configuration.set_no_of_rounds",
            "args": {
            "name": frm.doc.name 
            }
        })
        .success(success => {
            console.log(success)
        })
    },
    setup: function(frm) {
        frm.set_query('designation', () => {
            return {
                query: 'ethal.ethal.doctype.interview_configuration.interview_configuration.get_designation'
            }
        })
    }
});