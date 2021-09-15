import frappe

def execute():
    path = frappe.get_app_path("ethal", "patches", "imports", "workflow_action_master.csv")
    frappe.core.doctype.data_import.data_import.import_file("Workflow Action Master", path, "Insert", console=True)
