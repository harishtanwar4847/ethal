import frappe
from frappe.utils import getdate, nowdate, cint, flt
import json
from datetime import date, timedelta, datetime
import time
from frappe.utils import formatdate
import ast
import itertools
from frappe.utils import get_url_to_form

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
def purchase_invoice_item_tax(doc, method):
    if not doc.taxes_and_charges or "VAT" not in doc.taxes_and_charges:
        for i in doc.items:
            i.vat_amount = 0
    elif "VAT" in  doc.taxes_and_charges:
        for i in doc.items:
            i.vat_amount = (i.amount*15)/100


@frappe.whitelist()
def set_approver_name_and_sent_mail(doc, method):
    doc.approver_person = doc.modified_by
    doc.approver_date = doc.modified
    if doc.workflow_state == "Approved":
        owner = doc.owner
        approver = doc.approver_person
        doc_name = get_url_to_form(doc.doctype,doc.name)
        owner_na = frappe.get_doc("User",doc.owner)
        owner_name = owner_na.full_name
        approver_na = frappe.get_doc("User",doc.approver_person)
        approver_name = approver_na.full_name
        msg1= """ Hi {} and {},<br><br>
        Booked Sales invoice ID(Link) : {} ,<br><br>""".format(owner_name,approver_name,doc_name)
        msg2 = """Below are the item which are overweight than its marked weight.<br><br>
        <table border="1" cellspacing="0" cellpadding="5" align="center">
        <tr><th>Item Code</th><th>Item Name</th><th><p>Total Weight <br>[Weight per unit(added in item master)* quantity] </p></th><th><P>Total Net Weight <br>(added manually in sales invoice)</P></th><th><P>Difference <br>(In %)</P></th><th> Over/Under </th></tr>"""
        for item in doc.items:
            if item.total_net_weight > item.total_weight:
                msg2 +="<tr align='center'><td>"+item.item_code+"</td><td>"+ item.item_name+"</td><td>"+ str(item.total_weight)+"</td><td>"+ str(item.total_net_weight)+"</td><td>"+str(round(((item.total_net_weight*100)/(item.total_weight )if item.total_weight !=0 else 0)-(100),2))+"</td>"
                if item.total_weight ==0:
                    msg2+= "<td>"+'Update weight per unit in item master to get the result'+"</td></tr>"
                else:
                    msg2+="<td>"+'over weight' +"</td></tr>"

        msg2 +="</table><br>"
        msg3="""Thanks and Regards"""
        msg=msg1+msg2+msg3 
        frappe.sendmail(recipients=[owner,approver], sender="support-ethal-atri-erp@atriina.com", subject="<Alert>Item weight greater than its original weight", message=msg)

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
    if len(doc.fs_number) > 8 or len(doc.fs_number) < 8:
        frappe.throw('FS Number should be 8 digits')
    naming_series = doc.naming_series.split('.')
    fs_number = frappe.db.get_all('FS Number Period', {'series': doc.naming_series, 'company': doc.company, 'status': 'Active', 'docstatus': 1}, ['start_date', 'end_date', 'name'], limit=1, order_by='name desc')
    if fs_number:
        if fs_number[0]['end_date'] == None:
            if datetime.strptime(doc.posting_date, '%Y-%m-%d').date() >= fs_number[0]['start_date']:
                sales_invoice = frappe.db.get_value('Sales Invoice', {'posting_date': ['>=', fs_number[0]['start_date']], 'fs_number': doc.fs_number, 'naming_series': ['like', '%'+naming_series[0]+'%'], 'docstatus': ['!=', '2']}, ['name'])
                posting_date = frappe.db.get_value('Sales Invoice', {'posting_date': ['>=', fs_number[0]['start_date']], 'fs_number': doc.fs_number, 'naming_series': ['like', '%'+naming_series[0]+'%'], 'docstatus': ['!=', '2']}, ['posting_date'])
                if sales_invoice == None:
                    return
                else:
                    if sales_invoice != doc.name:    
                        frappe.throw('FS Numer must be unique')
        else:
            if datetime.strptime(doc.posting_date, '%Y-%m-%d').date() <= fs_number[0]['end_date'] and datetime.strptime(doc.posting_date, '%Y-%m-%d').date() >= fs_number[0]['start_date']:
                sales_invoice = frappe.db.get_value('Sales Invoice', {'posting_date': ['<=', fs_number[0]['end_date']], 'posting_date': ['>=', fs_number[0]['start_date']], 'fs_number': doc.fs_number, 'naming_series': ['like', '%'+naming_series[0]+'%'], 'docstatus': ['!=', '2']}, ['name'])
                posting_date = frappe.db.get_value('Sales Invoice', {'posting_date': ['<=', fs_number[0]['end_date']], 'posting_date': ['>=', fs_number[0]['start_date']], 'fs_number': doc.fs_number, 'naming_series': ['like', '%'+naming_series[0]+'%'], 'docstatus': ['!=', '2']}, ['posting_date'])
                if sales_invoice == None:
                    return
                else:
                    if sales_invoice != doc.name:    
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
                and po.transaction_date Between DATE_SUB(CURDATE(), INTERVAL 6  MONTH) and CURDATE() 
                and po.name != '{}'
        """.format(items['item_code'], doc.name), debug=1)
        frappe.db.set_value('Purchase Order Item', {'parent': doc.name, 'item_code': items['item_code']}, 'average_price', average_price[0][0]) 
        frappe.db.commit()  