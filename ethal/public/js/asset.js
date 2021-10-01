frappe.ui.form.on('Asset', {
	refresh(frm) {
		frm.add_custom_button(__('Task'), function(){
            //perform desired action such as routing to new form or fetching etc.
            
            let d = new frappe.ui.form.MultiSelectDialog({
                doctype: "Asset Maintenance Log",
                target: frm.doc,
                setters: {
                    // schedule_date: null,
                    task_name: '',
                    maintenance_status: '',
                    due_date: null
                },
                primary_action_label: "Mark as Complete",
                // add_filters_group: 1,
                // date_field: "transaction_date",
                get_query() {
                    return {
                        filters: { 
                            docstatus: ["!=", 2], 
                            asset_name: frm.doc.name
                        }   
                    }
                },
                action(selections) {
                    for (var i in selections){
                        frappe.call({
                            method: 'ethal.utils.update_maitenance_log',
                            args: {
                                name: selections[i]
                            }
                        })
                    }
                    cur_dialog.hide();
                }
            });
        });          
	}
})