frappe.ui.form.on('Customer', {
	refresh:function(frm) {
        frm.set_df_property('tax_id', 'reqd', 1)
	}
})