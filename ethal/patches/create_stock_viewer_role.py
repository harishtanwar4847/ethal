import frappe

def execute():
    try:
        frappe.get_doc({
            'doctype': 'Role',
            'role_name': 'Stock Viewer',
        }).insert()
        frappe.db.commit()
    except frappe.DuplicateEntryError:
        pass
