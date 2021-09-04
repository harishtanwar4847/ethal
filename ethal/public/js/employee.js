frappe.ui.form.on('Employee', {
	refresh(frm) {
	    console.log('refresh')
		// your code here
// 		frm.clear_table("employee_prerequisite"); 
// 		frm.refresh_field('employee_prerequisite');
		if(frm.doc.employee_prerequisite == undefined || frm.doc.employee_prerequisite == ''){
		    frappe.db.get_list('Employee Prerequisite Document', {
                    fields: ['name'],
                        }).then(records => {
                            console.log(records);
                            for (var j = 0; j < records.length; j++) {
                                console.log(records[j].name)
                                var childTable = cur_frm.add_child("employee_prerequisite");
                                childTable.document_type = records[j].name
                            }
                    cur_frm.refresh_fields("employee_prerequisite");
                    cur_frm.save()
                })
		}
	}
})