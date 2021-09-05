frappe.ui.form.on('Job Opening', {
	refresh(frm) {
		// your code here
		var today = new Date();
        var dd = String(today.getDate()).padStart(2, '0');
        var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
        var yyyy = today.getFullYear();
        today = yyyy + '-' + mm + '-' + dd;
        console.log(today)
        console.log(frm.doc.end_date)
        if (frm.doc.end_date > today) {
            console.log("helloooooooooo")
            frm.set_value('status', 'Closed')
           
        }
	}
})