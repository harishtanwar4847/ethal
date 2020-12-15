// Copyright (c) 2020, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Interview', {
	// refresh: function(frm) {

	// }
	job_applicant: function(frm) {
        frm.set_value('job_opening', null)
        frm.set_value('designation', null)

        if (frm.doc.job_applicant) {
            frappe.call({
                    method: "ethal.ethal.doctype.interview.interview.get_job_applicant_details",
                    args: {
                        job_applicant_name: frm.doc.job_applicant
                    }
                })
                .success(success => {
                    console.log(success)
                    frm.set_value('job_opening', success.message.job_opening)
                    frm.set_value('designation', success.message.designation)
                })
        }
    }
});