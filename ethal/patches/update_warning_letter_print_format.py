import frappe

def execute():
    path = frappe.get_app_path("ethal", "patches", "imports", "update_warning_letter_print_format.csv")
    frappe.core.doctype.data_import.data_import.import_file("Print Format", path, "Update Existing Records", console=True)
