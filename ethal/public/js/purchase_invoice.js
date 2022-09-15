frappe.ui.form.on("Purchase Invoice Item", "item_code", function(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
        frappe.db.get_value("Item", {"name": d.item_code}, "item_group", function(value) {
            if (value.item_group == "SERVICES"){
                d.type_of_purchase = "Services";
            }
            else(
                d.type_of_purchase = "Purchase"
            )
            
        });
});