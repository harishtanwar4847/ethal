import frappe
from frappe.utils import getdate, nowdate, cint, flt
import json
from datetime import date, timedelta, datetime
import time
from frappe.utils import formatdate
import ast
import itertools

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

@frappe.whitelist()
def before_insert_payment_entry(doc, method):
    if doc.naming_series.startswith('CPV') and doc.mode_of_payment == 'Cheque':
        payment_entries = frappe.db.get_value('Payment Entry', {'reference_no': doc.reference_no, 'docstatus': ['!=', '2']}, ['name'])
        if payment_entries == None:
            return
        elif payment_entries != doc.name:    
            frappe.throw('Cheque/Reference no must be unique')   

def before_insert_sales_invoice(doc, method):
    naming_series = doc.naming_series.split('.')
    sales_invoice = frappe.db.get_value('Sales Invoice', {'fs_number': doc.fs_number, 'naming_series': ['like', '%'+naming_series[0]+'%'], 'docstatus': ['!=', '2']}, ['name'])
    if sales_invoice == None:
        return
    elif sales_invoice != doc.name:    
        frappe.throw('FS Numer must be unique')   

def set_average_price(doc, method):
    year = datetime.strptime(doc.transaction_date, '%Y-%m-%d').year
    for items in frappe.get_all('Purchase Order Item', filters={'parent': doc.name}, fields=['*']):
        average_price = frappe.db.sql("""
                select coalesce(sum(poi.amount)/sum(poi.qty), 0) as average 
                from `tabPurchase Order Item` poi
                join `tabPurchase Order` po
                on po.name = poi.parent
                where po.docstatus = 1
                and poi.item_code = '{}'
                and year(po.transaction_date) = {}
                and po.name != '{}'
        """.format(items['item_code'], year, doc.name), debug=1)
        frappe.db.set_value('Purchase Order Item', {'parent': doc.name, 'item_code': items['item_code']}, 'average_price', average_price[0][0]) 
        frappe.db.commit()  