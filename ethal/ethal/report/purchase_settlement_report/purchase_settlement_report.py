# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	columns = get_column()
	data = get_data()
	return columns, data

def get_column():
    # columns = ["CPV Posting Date ::150"]+["Jv Posting Date ::150"]+["Voucher No CPV ::200"]+["Voucher No JV ::150"]+["Debit ::150"]+["Credit ::150"]+["Balance ::350"]+["Reference No ::150"]+["PO ::150"]+["PRF ::150"]+["GRN ::150"]+["Purchase Invoice ::150"]
	columns = [
		{
			"fieldname": "cpv_posting_date",
			"label": _("CPV Posting Date"),
			"fieldtype": "Date",
			"width": 150
		},
		{
			"fieldname": "jv_posting_date",
			"label": _("Jv Posting Date"),
			"fieldtype": "Date",
			"width": 150
		},
		{
			"fieldname": "voucher_no_cpv",
			"label": _("Voucher No CPV"),
			"fieldtype": "Link",
			"options": "Payment Entry",
			"width": 200
		},
		{
			"fieldname": "voucher_no_jv",
			"label": _("Voucher No JV"),
			"fieldtype": "Link",
			"options": "Journal Entry",
			"width": 200
		},
		{
			"fieldname": "debit",
			"label": _("Debit"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "credit",
			"label": _("Credit"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "balance",
			"label": _("Balance"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "reference_no",
			"label": _("Reference No"),
			"fieldtype": "Data",
			"width": 300
		},
		{
			"fieldname": "po",
			"label": _("PO"),
			"fieldtype": "Date",
			"options": "Purchase Order",
			"width": 150
		},
		{
			"fieldname": "prf",
			"label": _("PRF"),
			"fieldtype": "Link",
			"options": "Material Request",	
			"width": 150
		},
		{
			"fieldname": "grn",
			"label": _("GRN"),
			"fieldtype": "Link",
			"options": "Purchase Receipt",
			"width": 150
		},
		{
			"fieldname": "purchase_invoice",
			"label": _("Purchase Invoice"),
			"fieldtype": "Link",
			"options" : "Purchase Invoice",
			"width": 150
		}
	]
	return columns

def get_data():

	return frappe.db.sql("""
	select pe.posting_date, je.posting_date, pe.name, je.name, pe.paid_amount, je.total_debit, 
	(pe.paid_amount - je.total_debit), je.user_remark, pi.purchase_order, poi.material_request, pi.purchase_receipt, jea.reference_name
	from `tabPayment Entry` as pe 
	left join `tabJournal Entry` as je 
	on je.cheque_no = pe.name
	left join `tabJournal Entry Account` as jea
	on je.name = jea.parent
	left join `tabPurchase Invoice Item` as pi
	on jea.reference_name = pi.parent
	left join `tabPurchase Order Item` as poi
	on pi.purchase_order = poi.name
	where pe.paid_to like "%11210%"
	and je.docstatus = 1 and pe.docstatus = 1
	group by pe.name, je.name;
	""")