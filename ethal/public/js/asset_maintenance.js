frappe.ui.form.on('Asset Maintenance', {
	setup: (frm) => {
		frm.set_query("foreman_list", "asset_maintenance_tasks", function(doc) {
			return {
				query: "ethal.assets.get_team_members",
				filters: {
					maintenance_team: doc.maintenance_team
				}
			};
        });
    }    
});