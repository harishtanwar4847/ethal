import frappe

def execute():
    path = frappe.get_app_path("ethal", "patches", "imports", "shift_type.csv")
    frappe.core.doctype.data_import.data_import.import_file("Shift Type", path, "Insert", console=True)
