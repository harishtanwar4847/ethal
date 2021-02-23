frappe.listview_settings['Salary Structure Assignment'] = {
    add_fields: ["staus"],
    get_indicator: function(doc) {
        if(doc.staus=="Salary Updated") {
            return [__("Salary Updated"), "green", "staus,=,Salary Updated"];
        }
    }
}
