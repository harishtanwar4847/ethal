import frappe

def execute():
    try:
        frappe.get_doc({
            'doctype': 'Module Def',
            'app_name': 'ethal',
            'module_name': 'Assets Customizations'
        }).insert()
        frappe.db.commit()
    except frappe.DuplicateEntryError:
        pass
