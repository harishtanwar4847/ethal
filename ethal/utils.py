import frappe
from frappe.utils import getdate, nowdate, cint, flt
import json
from datetime import date, timedelta, datetime
import time
from frappe.utils import formatdate
import ast
import itertools
from erpnext.hr.doctype.employee_checkin.employee_checkin import mark_attendance_and_link_log
from frappe.utils.background_jobs import enqueue

@frappe.whitelist()
def before_save_asset_maintenance_log(doc, method):  
    asset_maintenance_task = frappe.get_all('Asset Maintenance Task', filters={'parent': doc.asset_maintenance}, fields=['maintanence_category', 'maintenance_task'])
    if asset_maintenance_task:
        for row in asset_maintenance_task:
            print(row['maintenance_task'])
            frappe.db.set_value('Asset Maintenance Log', {'task_name': row['maintenance_task']}, 'maintanence_category', row['maintanence_category'])

@frappe.whitelist()
def create_stock_entry(doc, method):
    get_part_used = frappe.get_all('Parts Used Item Table', filters = {'parent': doc.name}, fields=['*'])
    print(get_part_used)
    stock_entry = frappe.new_doc('Stock Entry')
    stock_entry.stock_entry_type= 'Material Issue'
    for row in get_part_used:
        source_warehouse = frappe.db.get_all('Item Default', {'parent': row['item']}, ['default_warehouse'])
        stock_entry.append('items', {
            's_warehouse': source_warehouse[0].default_warehouse,
            'item_code': row['item'],
            'item_group': row['item_group'],
            'qty': row['quantity'],
            'uom': row['uom']
        })
        stock_entry.insert(ignore_permissions=True)
        stock_entry.docstatus = 1

@frappe.whitelist()
def create_stock_entry_from_asset_repair(doc, method):
    get_part_used = frappe.get_all('Parts Used Item Table', filters = {'parent': doc.name}, fields=['*'])
    print(get_part_used)
    stock_entry = frappe.new_doc('Stock Entry')
    stock_entry.stock_entry_type= 'Material Issue'
    for row in get_part_used:
        source_warehouse = frappe.db.get_all('Item Default', {'parent': row['item']}, ['default_warehouse'])
        stock_entry.append('items', {
            's_warehouse': source_warehouse[0].default_warehouse,
            'item_code': row['item'],
            'item_group': row['item_group'],
            'qty': row['quantity'],
            'uom': row['uom']
        })
    stock_entry.insert(ignore_permissions=True)
    stock_entry.docstatus = 1

@frappe.whitelist()
def set_items_from_stock_entry(name):
    stock_entry_detail = frappe.get_all('Stock Entry Detail', filters={'parent': name}, fields=['*'])
    for i in stock_entry_detail:
        return i

@frappe.whitelist()
def before_submit_all_doctypes(doc, method):
    user = frappe.get_roles(frappe.session.user)
    admin_settings = frappe.get_doc('Admin Settings')
    admin_settings_document = frappe.get_all('Admin Settings Document', {'parent': 'Admin Settings', 'document': doc.doctype}, ['date'], as_list=1)  
   
    if admin_settings.applicable_for_role not in user:
        if admin_settings_document:
            if admin_settings_document[0][0] == 'posting_date':
                if admin_settings.closure_date > doc.posting_date:
                    frappe.throw(frappe._("You are not authorized to add or update entries before {0}").format(formatdate(admin_settings.closure_date)))
            elif admin_settings_document[0][0] == 'transaction_date':
                if admin_settings.closure_date > doc.transaction_date:
                    frappe.throw(frappe._("You are not authorized to add or update entries before {0}").format(formatdate(admin_settings.closure_date)))

@frappe.whitelist()
def set_approver_name(doc, method):
    doc.approver_person = doc.modified_by
    doc.approver_date = doc.modified

@frappe.whitelist()
def before_submit_stock_entry(doc, method):
    if doc.value_difference > 1:
        frappe.throw('Incoming Value not equal to Outgoing Value! Please Correct the rate.')
        
# @frappe.whitelist()
# def assign_salary_structure(doc, company=None, grade=None, department=None, designation=None,employee=None,
#         from_date=None, base=None, variable=None, income_tax_slab=None):
#     employees = get_employees(doc, company= company, grade= grade,department= department,designation= designation,name=employee)

#     if employees:
#         if len(employees) > 20:
#             frappe.enqueue(assign_salary_structure_for_employees, timeout=600,
#                 employees=employees, salary_structure=doc,from_date=from_date,
#                 base=base, variable=variable, income_tax_slab=income_tax_slab)
#         else:
#             assign_salary_structure_for_employees(employees, doc, from_date=from_date,
#                 base=base, variable=variable, income_tax_slab=income_tax_slab)
#     else:
#         frappe.msgprint(frappe._("No Employee Found"))

# def assign_salary_structure_for_employees(employees, salary_structure, from_date=None, base=None, variable=None, income_tax_slab=None):
# 	salary_structures_assignments = []
# 	existing_assignments_for = get_existing_assignments(employees, salary_structure, from_date)
# 	count=0
# 	for employee in employees:
# 		if employee in existing_assignments_for:
# 			continue
# 		count +=1

# 		salary_structures_assignment = create_salary_structures_assignment(employee,
# 			salary_structure, from_date, base, variable, income_tax_slab)
# 		salary_structures_assignments.append(salary_structures_assignment)
# 		frappe.publish_progress(count*100/len(set(employees) - set(existing_assignments_for)), title = frappe._("Assigning Structures..."))

# 	if salary_structures_assignments:
# 		frappe.msgprint(frappe._("Structures have been assigned successfully"))


# def create_salary_structures_assignment(employee, salary_structure, from_date, base, variable, income_tax_slab=None):
#     salary_structure = ast.literal_eval(salary_structure)
#     assignment = frappe.new_doc("Salary Structure Assignment")
#     assignment.employee = employee
#     assignment.salary_structure = salary_structure['name']
#     assignment.company = salary_structure['company']
#     assignment.from_date = from_date
#     assignment.base = base
#     assignment.variable = variable
#     assignment.income_tax_slab = income_tax_slab
#     assignment.save(ignore_permissions = True)
#     assignment.submit()
#     return assignment.name


# def get_existing_assignments(employees, salary_structure, from_date):
#     salary_structure = ast.literal_eval(salary_structure)
#     salary_structures_assignments = frappe.db.sql_list("""
#         select distinct employee from `tabSalary Structure Assignment`
#         where salary_structure=%s and employee in (%s)
#         and company= %s and docstatus=1
#     """ % ('%s', ', '.join(['%s']*len(employees)),'%s'), [salary_structure['name']] + employees+[salary_structure['company']])
#     if salary_structures_assignments:
#         frappe.msgprint(frappe._("Skipping Salary Structure Assignment for the following employees, as Salary Structure Assignment records already exists against them. {0}")
#             .format("\n".join(salary_structures_assignments)))
#     return salary_structures_assignments

@frappe.whitelist()
def make_salary_slip(source_name, target_doc = None, employee = None, as_print = False, print_format = None, for_preview=0, ignore_permissions=False):
	def postprocess(source, target):
		if employee:
			employee_details = frappe.db.get_value("Employee", employee,
				["employee_name", "branch", "designation", "department"], as_dict=1)
			target.employee = employee
			target.employee_name = employee_details.employee_name
			target.branch = employee_details.branch
			target.designation = employee_details.designation
			target.department = employee_details.department
		target.run_method('process_salary_structure', for_preview=for_preview)

	doc = get_mapped_doc("Salary Structure", source_name, {
		"Salary Structure": {
			"doctype": "Salary Slip",
			"field_map": {
				"total_earning": "gross_pay",
				"name": "salary_structure"
			}
		}
	}, target_doc, postprocess, ignore_child_tables=True, ignore_permissions=ignore_permissions)

	if cint(as_print):
		doc.name = 'Preview for {0}'.format(employee)
		return frappe.get_print(doc.doctype, doc.name, doc = doc, print_format = print_format)
	else:
		return doc


# def get_employees(doc, **kwargs):
# 		conditions, values = [], []
# 		for field, value in kwargs.items():
# 			if value:
# 				conditions.append("{0}=%s".format(field))
# 				values.append(value)

# 		condition_str = " and " + " and ".join(conditions) if conditions else ""

# 		employees = frappe.db.sql_list("select name from tabEmployee where status='Active' {condition}"
# 			.format(condition=condition_str), tuple(values))

# 		return employees


@frappe.whitelist()
def before_insert_payment_entry(doc, method):
    if doc.naming_series.startswith('CPV') and doc.mode_of_payment == 'Cheque':
        payment_entries = frappe.db.get_value('Payment Entry', {'reference_no': doc.reference_no, 'docstatus': ['!=', '2']}, ['name'])
        if payment_entries == None:
            return
        elif payment_entries != doc.name:    
            frappe.throw('Cheque/Reference no must be unique')   

def before_insert_sales_invoice(doc, method):
    if doc.naming_series.startswith('ACSI-TU'):
        sales_invoice = frappe.db.get_value('Sales Invoice', {'fs_number': doc.fs_number, 'naming_series': ['like', '%ACSI-TU-%'], 'docstatus': ['!=', '2']}, ['name'])
        if sales_invoice == None:
            return
        elif sales_invoice != doc.name:    
            frappe.throw('FS Numer must be unique')   
    elif doc.naming_series.startswith('ACSI-DB'):  
        sales_invoice = frappe.db.get_value('Sales Invoice', {'fs_number': doc.fs_number, 'naming_series': ['like', '%ACSI-DB-%'], 'docstatus': ['!=', '2']}, ['name'])
        if sales_invoice == None:
            return
        elif sales_invoice != doc.name:    
            frappe.throw('FS Numer must be unique')   