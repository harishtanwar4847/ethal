frappe.ui.form.on('Vehicle Log', {
	refresh(frm) {
        // your code here
        console.log('refresh')
	},
	odometer(frm){
	    console.log('jana')
	    frm.set_value('todays_total_unit_consumed', frm.doc.odometer - frm.doc.last_odometer)
	}
})