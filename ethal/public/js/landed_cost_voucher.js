frappe.ui.form.on('Landed Cost Voucher', {
	refresh(frm) {
        // your code here
	},
	import_cost_sheet(frm) {
	    if (frm.doc.import_cost_sheet) {
	        console.log('hello')
	        frappe.db.get_value('Import Cost Sheet', frm.doc.import_cost_sheet, 'net_total')
                .then(r => {
                    console.log(r.message.net_total) // Open
                     frm.doc.taxes[0].amount = r.message.net_total
	                 frm.refresh_field('taxes')
                })

	       
	    }
	}
})