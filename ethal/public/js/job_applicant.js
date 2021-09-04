frappe.ui.form.on('Job Applicant', {
    refresh: function (frm) {
        console.log('in refresh')
        cur_frm.set_df_property('job_title', 'fieldtype', 'Data');
        cur_frm.refresh_field('job_title')
        if (frm.doc.status != "Selected") {
            frm.remove_custom_button("Job Offer");
        }

        // console.log("Selected")
        // frm.remove_custom_button("Schedule Interview");
        //   }
        if (!frm.doc.__islocal) {
            frappe.call({
                'method': 'ethal.hr.existing_interview_rounds',
                'args': {
                    job_applicant: frm.doc.name,
                    job_opening: frm.doc.job_title
                }
            })

                .success(success => {
                    console.log(success.message);
                    if (success.message === true) {
                        frm.add_custom_button(__("Show Feedback"), function () {
                            frappe.call({
                                'method': 'ethal.hr.get_interview_rounds',
                                'args': {
                                    job_applicant: frm.doc.name,
                                    job_opening: frm.doc.job_title
                                }
                            })

                                .success(success => {
                                    console.log(success.message);
                                    locals.DocType['Interviewer'] = success.message.interviewer
                                    let d = new frappe.ui.Dialog({
                                        title: 'Interviewers Feedback',
                                        fields: success.message.interview_rounds,

                                        primary_action_label: 'Show Details',
                                        primary_action(values) {
                                            frappe.set_route("List", "Interview Round");
                                            console.log(values);
                                            d.hide();
                                        }
                                    });

                                    d.show();
                                });
                        });
                    }
                })
            if (frm.doc.status !== "Selected" && frm.doc.status !== "Offered" && frm.doc.status !== "Offer Accepted") {
                frm.add_custom_button(__("Schedule Interview"), function () {
                    frappe.call({
                        'method': 'ethal.hr.get_interview_and_interview_rounds',
                        'args': {
                            job_applicant: frm.doc.name,
                            job_opening: frm.doc.job_title
                        },
                        // disable the button until the request is completed
                        // btn: $('.primary-action'),
                        // freeze the screen until the request is completed
                        freeze: true,
                        error: (r) => {
                            // on error
                        },
                        callback: (r) => {
                            console.log(r.message);
                            if (r.message === false) {
                                frappe.msgprint({
                                    title: __('Notification'),
                                    message: __('Please Configure Interview process before Scheduling Interview'),

                                    primary_action: {
                                        'label': 'Create Interview Configuration',
                                        action(values) {
                                            frappe.set_route("Form", "Interview Configuration", "New Interview Configuration", {
                                                designation: cur_frm.doc.designation
                                            });
                                            console.log(values);
                                        }
                                    }
                                });
                            }
                            else {
                                locals.DocType['Interviewer'] = r.message.interviewer
                                let d = new frappe.ui.Dialog({
                                    title: 'Interview details',
                                    fields: r.message.rounds,

                                    primary_action_label: 'Save',
                                    primary_action(values) {
                                        console.log(isEmpty(values));
                                        if (isEmpty(values)) {
                                            d.hide();
                                            return;
                                        }
                                        else {
                                            ScheduleInterview(values, frm.doc.name);
                                            // console.log(values);
                                            d.hide();
                                        }
                                    }
                                });

                                d.show();
                            }
                        },
                    });
                });
            }
        }
        // on success
    },

});
function ScheduleInterview(values, job_applicant) {
    frappe.call({
        "method": "ethal.hr.save_interview_round",
        "args": {
            "formdata": values,
            "job_applicant": job_applicant
        }
    })
        .success(success => {
            console.log(typeof (success.message))
            msgprint("Interview has been scheduled....");
        })
}
function isEmpty(obj) {
    for (var key in obj) {
        if (obj.hasOwnProperty(key))
            return false;
    }
    return true;
}