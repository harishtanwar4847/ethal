import frappe
from frappe import _
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
@frappe.validate_and_sanitize_search_inputs
def get_team_members(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.get_values('Foremen List', { 'parent': filters.get("maintenance_team") }, ['foreman'])

def update_asset_task(doc, method):
    print('in custom method')
    sync_maintenance_tasks(doc)

def sync_maintenance_tasks(doc):
    asset = frappe.db.get_value('Asset', doc.name, 'asset_name')
    print(asset)
    tasks_names = []
    for task in doc.get('asset_maintenance_tasks'):
        print(task)
        tasks_names.append(task.name)
        update_asset_tasks(asset = asset, task = task, asset_maintenance = doc.name)
    asset_maintenance_logs = frappe.get_all("Asset Maintenance Log", fields=["name"], filters = {"asset_maintenance": doc.name,
        "task": ("not in", tasks_names)})
    if asset_maintenance_logs:
        for asset_maintenance_log in asset_maintenance_logs:
            maintenance_log = frappe.get_doc('Asset Maintenance Log', asset_maintenance_log.name)
            maintenance_log.db_set('maintenance_status', 'Cancelled')

def update_asset_tasks(asset, task, asset_maintenance):
    asset_task = frappe.get_value("Asset Task", {"asset": asset, 'asset_maintenance': asset_maintenance,
        "task": task.name, "status": ('in',['Planned','Overdue'])})

    if not asset_task:
        asset_task = frappe.get_doc({
            "doctype": "Asset Task",
            "asset_maintenance": asset_maintenance,
            "asset": asset,
            "task": task.name,
            "task_name": task.maintenance_task,
            "assign_to": task.assign_to,
            "assign_to_name": task.assign_to_name,
            "status": task.maintenance_status,
            "due_date": task.next_due_date
            # "periodicity": str(task.periodicity),
            # "maintenance_type": task.maintenance_type,
            # "due_date": task.next_due_date
        })
        asset_task.insert()
    else:
        update_task = frappe.get_doc('Asset Task', asset_task)
        update_task.task = task.name
        update_task.asset_maintenance = asset_maintenance
        update_task.task_name = task.maintenance_task
        update_task.assign_to = task.assign_to
        update_task.assign_to_name = task.assign_to_name
        update_task.status = task.maintenance_status
        update_task.due_date = task.next_due_date
        # update_task.periodicity = str(task.periodicity)
        # update_task.maintenance_type = task.maintenance_type
        # update_task.due_date = task.next_due_date
        update_task.save()

def asset_task_permission_query_conditions(user):
    print('=========================')
    user_roles = frappe.get_roles(user)
    print(user_roles)
    # supplier = frappe.get_all('Supplier', filters={'email_id': user}, fields=['name'], as_list = 1)
    # print(supplier)
    if 'System Manager' not in user_roles:
        return """(`tabAsset Task`.`assign_to`= '{0}' )""".format(frappe.session.user)

