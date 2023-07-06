frappe.ui.form.on("Purchase Order", {
 refresh(frm) {
    console.log(frappe.user.has_role("Purchase Order Approver"))
    if(frappe.user.has_role("Purchase Order Approver"))
    {
      set_field_options("naming_series", ["PO-DB-.YYYY.-","PO-HO-.YYYY.-",
        "PO-IMPORT-.YYYY.-"])
    }
    else
    {
      set_field_options("naming_series", ["PO-DB-.YYYY.-","PO-IMPORT-.YYYY.-"])
    }
    }
  });
  