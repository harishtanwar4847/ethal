import frappe

def execute():
    path = frappe.get_app_path("ethal", "patches", "imports", "employee_prerequisite_document.csv")
    frappe.core.doctype.data_import.data_import.import_file("Employee Prerequisite Document", path, "Insert", console=True)
