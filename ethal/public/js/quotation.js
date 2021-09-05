frappe.ui.form.on('Quotation', {
	refresh:function(frm) {
        console.log('refresh')
		frm.set_df_property('customer_address', 'reqd', 1)
		if (frm.doc.__islocal && frm.doc.valid_till && frm.doc.party_name) {
		    console.log('ja na e')
		    frm.set_value('valid_till', null)
		    frm.refresh()
		  //  frm.set_value('valid_till', frappe.datetime.add_months(doc.transaction_date, 1))
		}
	},
	copy_doc: function(frm){
	    console.log("helo", frm.doc)
	}
})