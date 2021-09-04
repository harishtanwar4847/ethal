
frappe.ui.form.on('Payment Entry', {
    
    refresh: function(frm) {
        console.log('refresh')
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
 
     },
     settlement_responsibility: function(frm) {
         if (!frm.doc.settlement_responsibility) {
             frm.set_value('settlement_responsible', '')
         }
     },
     party: function(frm) {
         if(!frm.doc.party){
             frm.set_value('payee_name', '')
             frm.set_value('party_name', '')
         }
     }
 
 })    