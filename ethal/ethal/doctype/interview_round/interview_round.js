// Copyright (c) 2020, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Interview Round', {
	refresh: function (frm) {
        if (frm.doc.__islocal) {
            frm.toggle_display('feedback_section', false)
            frm.toggle_display('status_section', false)
        }
        else {
            frappe.call({
                'method': 'ethal.ethal.doctype.interview_round.interview_round.previous_interview_rounds',
                'args': {
                    interview: frm.doc.interview,
                    interview_round: frm.doc.name
                    }
             })
                .success(success => {
                    console.log(success);
                    if (success.message != "No Rounds") {
                    frm.add_custom_button(__("Candidate History"), function() {
                        
                        let d = new frappe.ui.Dialog({
                        title: 'Interviewers Feedback',
                        fields: success.message,
        
                    });
                    
                        d.show();                    
                    })
                }
            })
        }
        frappe.model.get_value('Employee', {'user_id': frappe.session.user}, 'name',
        function(d) {   
          for (var i in frm.doc.interviewers) {
            if (frm.doc.interviewers[i].employee == d.name) {   
              console.log(frm.doc.interviewers[i]); // {a: 5, b: 6}
              frm.get_field("feedback").grid.toggle_reqd("remark", true);
              frm.set_df_property('overall_recommendation', 'reqd', 1);
              frm.get_field("feedback").grid.toggle_reqd("rating1", true);
              frm.get_field("feedback").grid.toggle_reqd("skill", true);
              $(".grid-add-row").hide();
              $(".sortable-handle").hide();
            }
          } 
        })
            
    },
    feedback_on_form_rendered: function(frm, cdt, cdn){
        frappe.model.get_value('Employee', {'user_id': frappe.session.user}, 'name',
        function(d) {
          console.log(d.name)
          if(d.name == frm.doc.interviewers) {
            frm.fields_dict["feedback"].grid.wrapper.find('.grid-delete-row').hide();
            frm.fields_dict["feedback"].grid.wrapper.find('.grid-insert-row-below').hide();
            frm.fields_dict["feedback"].grid.wrapper.find('.grid-insert-row').hide();
            frm.fields_dict["feedback"].grid.wrapper.find('.grid-duplicate-row').hide();
            frm.fields_dict["feedback"].grid.wrapper.find('.grid-move-row').hide();
            }
        })
    },
    // before_save: function(frm){
       
    // },    
    after_save: function (frm) {
        frappe.call({
            "method": "ethal.ethal.doctype.interview.interview.set_rounds",
            "args": {
                interview: frm.doc.interview,
                round: frm.doc.round,
                designation: frm.doc.designation,
                name: frm.doc.name
            }
        })
            .success(success => {
                console.log(success)
            })
            frappe.model.get_value('Employee', {'user_id': frappe.session.user}, 'name',
            function(d) {
              console.log(d.name)
              if(d.name == frm.doc.interviewers) {
                    msgprint("Your Feedback has been submitted")
              }
            })
    },
    overall_recommendation: function(frm){
        if((frm.doc.overall_recommendation == 'Good Hire') || (frm.doc.overall_recommendation =='Strong Hire' )){
            frm.set_value('status', "Selected")
            console.log("hello")
        }
        else{
            frm.set_value('status', 'Rejected')
        }
        // frm.set_value('')
    },
    // round: function(frm) {
    //     if (frm.round) {
    //         frappe.call({
    //                 "method": "ethal.ethal.doctype.interview_round.interview_round.set_round_number_and_feedback",
    //                 "args": {
    //                     interview: frm.doc.interview,
    //                     round: frm.doc.round,
    //                     designation: frm.doc.designation,
    //                     name: frm.doc.name
    //                 }
    //             })
    //             .success(success => {
    //                 console.log(success)
    //                 frm.set_value("round_number", success.message[0])
    //                 for (var i = 0; i < success.message[1].length; ++i) {
    //                     frm.add_child('feedback', {
    //                         skill: success.message[1][i][0],
    //                     })
    //                 }
    //                 frm.refresh_field('feedback');
    //             })
    //     }
    // },
    setup: function (frm) {
        frm.set_query('round', () => {
            return {
                query: 'ethal.ethal.doctype.interview_round.interview_round.get_rounds',
                filters: {
                    interview: frm.doc.interview || null
                }
            }
        })
        frm.set_query("interviewers", function() {
            return {
                query: "ethal.ethal.doctype.interview_round.interview_round.get_interviewer"
            }
        });
    }
});