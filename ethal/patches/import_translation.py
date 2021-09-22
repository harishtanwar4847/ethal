import frappe

def execute():
    path = frappe.get_app_path("ethal", "patches", "imports", "translation.csv")
    frappe.core.doctype.data_import.data_import.import_file("Translation", path, "Insert", console=True)
