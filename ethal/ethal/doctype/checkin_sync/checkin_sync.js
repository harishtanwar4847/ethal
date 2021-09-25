// Copyright (c) 2021, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Checkin Sync', {
	refresh: function(frm) {
		if (frm.doc.attach_file.trim()) {
			frm.add_custom_button(__('Sync Checkins'), function(){
				return frappe.call({				
				method: 'ethal.checkins.create_checkins',
				freeze: true,
				freeze_message: "Syncing Checkins",
					callback: function(r) {
						frm.refresh();					
					}
				});
		  	});
		}  
	}
});
