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