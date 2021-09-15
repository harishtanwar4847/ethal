import frappe

def execute():
    path = frappe.get_app_path("ethal", "patches", "imports", "workflow_state.csv")
    frappe.core.doctype.data_import.data_import.import_file("Workflow State", path, "Insert", console=True)
