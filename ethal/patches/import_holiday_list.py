import frappe

def execute():
    path = frappe.get_app_path("ethal", "patches", "imports", "holiday_list.csv")
    frappe.core.doctype.data_import.data_import.import_file("Holiday List", path, "Insert", console=True)
