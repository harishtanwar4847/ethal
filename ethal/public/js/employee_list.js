frappe.listview_settings['Employee'] = {
	add_fields: ["warnings_status"],
	get_indicator: function(doc) {
		if(doc.warnings_status == '1'){
            return [__("1"), "green", "warnings_status,=,1"];
        }
        if(doc.warnings_status == '2'){
            return [__("2"), "orange", "warnings_status,=,2"];
        }
        if(doc.warnings_status == '3'){
            return [__("3"), "red", "warnings_status,=,3"];
        }
	}
};