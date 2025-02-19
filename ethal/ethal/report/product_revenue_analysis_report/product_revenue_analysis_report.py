# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate
from frappe import _

class Percent(int):
    def __str__(self):
        return '{:.2%}'.format(self)

def execute(filters=None):
	if not filters: filters ={}
	data = []
	conditions = get_columns(filters, "Sales Invoice")
	data = get_data(filters, conditions)

	return conditions["columns"], data

def get_columns(filters, trans):
	validate_filters(filters)

	# get conditions for based_on filter cond
	based_on_details = based_wise_columns_query(filters.get("based_on"), trans)
	# get conditions for periodic filter cond
	period_cols, period_select = period_wise_columns_query(filters, trans)
	# get conditions for grouping filter cond
	group_by_cols = group_wise_column(filters.get("group_by"))

	columns = based_on_details["based_on_cols"] + period_cols + [_("Total(Qty)") + ":Float:120", _("Total(Amt)") + ":Currency:120"]
	if group_by_cols:
		columns = based_on_details["based_on_cols"] + group_by_cols + period_cols + \
			[_("Total(Qty)") + ":Float:120", _("Total(Amt)") + ":Currency:120"]

	conditions = {"based_on_select": based_on_details["based_on_select"], "period_wise_select": period_select,
		"columns": columns, "group_by": based_on_details["based_on_group_by"], "grbc": group_by_cols, "trans": trans,
		"addl_tables": based_on_details["addl_tables"], "addl_tables_relational_cond": based_on_details.get("addl_tables_relational_cond", "")}

	return conditions

def validate_filters(filters):
	for f in ["Fiscal Year", "Based On", "Period", "Company"]:
		if not filters.get(f.lower().replace(" ", "_")):
			frappe.throw(_("{0} is mandatory").format(f))

	if not frappe.db.exists("Fiscal Year", filters.get("fiscal_year")):
		frappe.throw(_("Fiscal Year {0} Does Not Exist").format(filters.get("fiscal_year")))

	if filters.get("based_on") == filters.get("group_by"):
		frappe.throw(_("'Based On' and 'Group By' can not be same"))

def get_data(filters, conditions):
	data = []
	inc, cond= '',''
	query_details =  conditions["based_on_select"] + conditions["period_wise_select"]

	posting_date = 't1.transaction_date'
	if conditions.get('trans') in ['Sales Invoice', 'Purchase Invoice', 'Purchase Receipt', 'Delivery Note']:
		posting_date = 't1.posting_date'
		if filters.period_based_on:
			posting_date = 't1.'+filters.period_based_on

	if conditions["based_on_select"] in ["t1.project,", "t2.project,"]:
		cond = ' and '+ conditions["based_on_select"][:-1] +' IS Not NULL'
	if conditions.get('trans') in ['Sales Order', 'Purchase Order']:
		cond += " and t1.status != 'Closed'"

	if conditions.get('trans') == 'Quotation' and filters.get("group_by") == 'Customer':
		cond += " and t1.quotation_to = 'Customer'"

	year_start_date, year_end_date = frappe.db.get_value("Fiscal Year",
		filters.get('fiscal_year'), ["year_start_date", "year_end_date"])

	if filters.get("group_by"):
		sel_col = ''
		ind = conditions["columns"].index(conditions["grbc"][0])

		if filters.get("group_by") == 'Item':
			sel_col = 't2.item_code'
		elif filters.get("group_by") == 'Customer':
			sel_col = 't1.party_name' if conditions.get('trans') == 'Quotation' else 't1.customer'
		elif filters.get("group_by") == 'Supplier':
			sel_col = 't1.supplier'

		if filters.get('based_on') in ['Item','Customer','Supplier']:
			inc = 2
		else :
			inc = 1
		data1 = frappe.db.sql(""" select %s from `tab%s` t1, `tab%s Item` t2 %s
					where t2.parent = t1.name and t1.company = %s and %s between %s and %s and
					t1.docstatus = 1 %s %s
					group by %s
				""" % (query_details,  conditions["trans"],  conditions["trans"], conditions["addl_tables"], "%s",
					posting_date, "%s", "%s", conditions.get("addl_tables_relational_cond"), cond, conditions["group_by"]), (filters.get("company"),
					year_start_date, year_end_date),as_list=1)

		for d in range(len(data1)):
			#to add blanck column
			dt = data1[d]
			dt.insert(ind,'')
			data.append(dt)

			#to get distinct value of col specified by group_by in filter
			row = frappe.db.sql("""select DISTINCT(%s) from `tab%s` t1, `tab%s Item` t2 %s
						where t2.parent = t1.name and t1.company = %s and %s between %s and %s
						and t1.docstatus = 1 and %s = %s %s %s
					""" %
					(sel_col,  conditions["trans"],  conditions["trans"], conditions["addl_tables"],
						"%s", posting_date, "%s", "%s", conditions["group_by"], "%s", conditions.get("addl_tables_relational_cond"), cond),
					(filters.get("company"), year_start_date, year_end_date, data1[d][0]), as_list=1)

			for i in range(len(row)):
				des = ['' for q in range(len(conditions["columns"]))]

				#get data for group_by filter
				row1 = frappe.db.sql(""" select %s , %s from `tab%s` t1, `tab%s Item` t2 %s
							where t2.parent = t1.name and t1.company = %s and %s between %s and %s
							and t1.docstatus = 1 and %s = %s and %s = %s %s %s
						""" %
						(sel_col, conditions["period_wise_select"], conditions["trans"],
							conditions["trans"], conditions["addl_tables"], "%s", posting_date, "%s","%s", sel_col,
							"%s", conditions["group_by"], "%s", conditions.get("addl_tables_relational_cond"), cond),
						(filters.get("company"), year_start_date, year_end_date, row[i][0],
							data1[d][0]), as_list=1)

				des[ind] = row[i][0]

				for j in range(1,len(conditions["columns"])-inc):
					des[j+inc] = row1[0][j]

				data.append(des)
	else:
		data = frappe.db.sql(""" select %s from `tab%s` t1, `tab%s Item` t2 %s
					where t2.parent = t1.name and t1.company = %s and %s between %s and %s and
					t1.docstatus = 1 %s %s
					group by %s
				""" %
				(query_details, conditions["trans"], conditions["trans"], conditions["addl_tables"],
					"%s", posting_date, "%s", "%s", cond, conditions.get("addl_tables_relational_cond", ""), conditions["group_by"]),
				(filters.get("company"), year_start_date, year_end_date), as_list=1)
	str = 'Total'
	total = 	"\033[1m" + str + "\033[0m"
	list_total = ['Total', '']		
	if filters.get("period") == 'Yearly':
		year = 0
		qty = 0
		
		for k in data:
			qty += k[2] if k[2] != None else 0
			k[4] = k[3]/k[2] if k[2] != 0 else 0
		list_total.append(qty)
		amt = 0
		for k in data:
			amt += k[3] if k[3] != None else 0
		list_total.append(amt)
		rate = 0
		for j in data:
			rate += j[4] if j[4] != None else 0
		list_total.append(rate)	
		list_total.append('100')
		total_qty = 0
		for k in data:
			total_qty += k[6] if k[6] != None else 0
		list_total.append(total_qty)
		total_amt = 0
		for k in data:
			total_amt += k[7] if k[7] != None else 0
		list_total.append(total_amt)
		for i in data:
			year += i[3]	
		for j in data:
			j[5] = '{:.2f}%'.format((j[3]/year)*100)
	elif filters.get("period") == 'Half-Yearly':
		jan_jun, jul_dec = 0, 0
		qty = 0
		for k in data:	
			k[3] = k[3] if k[3] != None else 0
			k[2] = k[2] if k[2] != None else 0
			k[4] = k[3]/k[2] if k[2] != 0 else 0
			qty += k[2] if k[2] != None else 0
		list_total.append(qty)
		amt = 0
		for k in data:
			k[7] = k[7] if k[7] != None else 0
			k[6] = k[6] if k[6] != None else 0
			k[8] = k[7]/k[6] if k[6] != 0 else 0
			amt += k[3] if k[3] != None else 0
		list_total.append(amt)
		rate = 0
		for k in data:
			rate += k[4] if k[4] != None else 0
		list_total.append(rate)
		list_total.append('100')
		total_qty = 0
		for k in data:
			total_qty += k[6] if k[6] != None else 0
		list_total.append(total_qty)
		total_amt = 0
		for k in data:
			total_amt += k[7] if k[7] != None else 0
		list_total.append(total_amt)
		total_rate = 0
		for k in data:
			total_rate += k[8] if k[8] != None else 0
		list_total.append(total_rate)
		list_total.append('100')
		for k in data:
			qty += k[9] if k[9] != None else 0
		list_total.append(qty)
		amt = 0
		for k in data:
			amt += k[10] if k[10] != None else 0
		list_total.append(amt)
		for i in data:
			jan_jun += i[3]	if i[3] != None else 0
			jul_dec += i[7]	if i[7] != None else 0	
		for j in data:
			j[5] = '{:.2f}%'.format((j[3]/jan_jun)*100) if j[3] != 0 else 0
			j[9] = '{:.2f}%'.format((j[7]/jul_dec)*100) if j[7] != 0 else 0 		
	elif filters.get("period") == 'Quarterly':
		jan_mar, apr_jun, jul_sep, oct_dec = 0, 0, 0, 0
		qty = 0
		for k in data:	
			k[3] = k[3] if k[3] != None else 0
			k[2] = k[2] if k[2] != None else 0
			k[4] = k[3]/k[2] if k[2] != 0 else 0
			qty += k[2] if k[2] != None else 0
		list_total.append(qty)
		amt = 0
		for k in data:
			amt += k[3] if k[3] != None else 0
			k[7] = k[7] if k[7] != None else 0
			k[6] = k[6] if k[6] != None else 0
			k[8] = k[7]/k[6] if k[6] != 0 else 0
		list_total.append(amt)
		total_rate = 0
		for k in data:
			k[10] = k[10] if k[10] != None else 0
			k[11] = k[11] if k[11] != None else 0
			k[12] = k[11]/k[10] if k[10] != 0 else 0
			total_rate += k[4] if k[4] != None else 0
		list_total.append(total_rate)
		list_total.append('100')
		total_qty = 0
		for k in data:
			total_qty += k[6] if k[6] != None else 0
		list_total.append(total_qty)
		total_amt = 0
		for k in data:
			total_amt += k[7] if k[7] != None else 0
		list_total.append(total_amt)
		total_amt = 0
		for k in data:
			total_amt += k[8] if k[8] != None else 0
		list_total.append(total_amt)
		list_total.append('100')
		for k in data:
			k[15] = k[15] if k[15] != None else 0
			k[14] = k[14] if k[14] != None else 0
			k[16] = k[15]/k[14] if k[14] != 0 else 0
			qty += k[10] if k[10] != None else 0
		list_total.append(qty)
		qty = 0
		for k in data:	
			qty += k[11] if k[11] != None else 0
		list_total.append(qty)
		total_amt = 0
		for k in data:
			total_amt += k[12] if k[12] != None else 0
		list_total.append(total_amt)
		list_total.append('100')
		amt = 0
		for k in data:
			amt += k[14] if k[14] != None else 0
		list_total.append(amt)
		total_qty = 0
		for k in data:
			total_qty += k[15] if k[15] != None else 0
		list_total.append(total_qty)
		total_amt = 0
		for k in data:
			total_amt += k[16] if k[16] != None else 0
		list_total.append(total_amt)
		list_total.append('100')
		total_amt = 0
		for k in data:
			total_amt += k[15] if k[15] != None else 0
		list_total.append(total_amt)
		for k in data:
			qty += k[16] if k[16] != None else 0
		list_total.append(qty)
		list_total.append('100')
		for i in data:
			jan_mar += i[3] if i[3] != None else 0
			apr_jun += i[7] if i[7] != None else 0
			jul_sep += i[11] if i[11] != None else 0 		
			oct_dec += i[15] if i[15] != None else 0
		for j in data:
			j[5] =  '{:.2f}%'.format((j[3]/jan_mar)*100) if j[3] != 0 else 0
			j[9] =  '{:.2f}%'.format((j[7]/apr_jun)*100)  if j[7] != 0 else 0
			j[13] =  '{:.2f}%'.format((j[11]/jul_sep)*100) if j[11] != 0 else 0
			j[17] =  '{:.2f}%'.format((j[15]/oct_dec)*100) if j[15] != 0 else 0	
	elif filters.get("period") == 'Monthly':		
		jan , feb , mar, apr, may, jun, july, aug, sep, oct, nov, dec = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0
		qty = 0
		for k in data:	
			qty += k[2] if k[2] != None else 0
			k[3] = k[3] if k[3] != None else 0
			k[2] = k[2] if k[2] != None else 0
			k[4] = k[3]/k[2] if k[2] != 0 else 0
		list_total.append(qty)
		amt = 0
		for k in data:
			amt += k[3] if k[3] != None else 0
			k[10] = k[10] if k[10] != None else 0
			k[11] = k[11] if k[11] != None else 0
			k[12] = k[11]/k[10] if k[10] != 0 else 0
		list_total.append(amt)
		total_rate = 0
		for k in data:
			k[6] = k[6] if k[6] != None else 0
			k[7] = k[7] if k[7] != None else 0
			k[8] = k[7]/k[6] if k[6] != 0 else 0
			total_rate += k[4] if k[4] != None else 0
		list_total.append(total_rate)
		list_total.append('100')
		total_qty = 0
		for k in data:
			total_qty += k[6] if k[6] != None else 0
		list_total.append(total_qty)
		total_amt = 0
		for k in data:
			total_amt += k[7] if k[7] != None else 0
		list_total.append(total_amt)
		total_amt = 0
		for k in data:
			total_amt += k[8] if k[8] != None else 0
		list_total.append(total_amt)
		list_total.append('100')
		for k in data:
			qty += k[10] if k[10] != None else 0
		list_total.append(qty)
		qty = 0
		for k in data:	
			qty += k[11] if k[11] != None else 0
			k[14] = k[14] if k[14] != None else 0
			k[15] = k[15] if k[15] != None else 0
			k[16] = k[15]/k[14] if k[14] != 0 else 0
		list_total.append(qty)
		total_amt = 0
		for k in data:
			total_amt += k[12] if k[12] != None else 0
		list_total.append(total_amt)
		list_total.append('100')
		amt = 0
		for k in data:
			amt += k[14] if k[14] != None else 0
			k[18] = k[18] if k[18] != None else 0
			k[19] = k[19] if k[19] != None else 0
			k[20] = k[19]/k[18] if k[18] != 0 else 0
		list_total.append(amt)
		total_qty = 0
		for k in data:
			total_qty += k[15] if k[15] != None else 0
		list_total.append(total_qty)
		total_amt = 0
		for k in data:
			total_amt += k[16] if k[16] != None else 0
		list_total.append(total_amt)
		list_total.append('100')
		total_amt = 0
		for k in data:
			total_amt += k[18] if k[18] != None else 0
			k[22] = k[22] if k[22] != None else 0
			k[23] = k[23] if k[23] != None else 0
			k[24] = k[23]/k[22] if k[22] != 0 else 0
		list_total.append(total_amt)
		for k in data:
			qty += k[19] if k[19] != None else 0
		list_total.append(qty)
		total_amt = 0
		for k in data:
			total_amt += k[20] if k[20] != None else 0
		list_total.append(total_amt)
		list_total.append('100')
		qty = 0
		for k in data:	
			qty += k[22] if k[22] != None else 0
		list_total.append(qty)
		amt = 0
		for k in data:
			amt += k[23] if k[23] != None else 0
			k[26] = k[26] if k[26] != None else 0
			k[27] = k[27] if k[27] != None else 0
			k[28] = k[27]/k[26] if k[26] != 0 else 0
		list_total.append(amt)
		total_amt = 0
		for k in data:
			total_amt += k[24] if k[24] != None else 0
		list_total.append(total_amt)
		list_total.append('100')
		total_qty = 0
		for k in data:
			total_qty += k[26] if k[26] != None else 0
		list_total.append(total_qty)
		total_amt = 0
		for k in data:
			total_amt += k[27] if k[27] != None else 0
			k[30] = k[30] if k[30] != None else 0
			k[31] = k[31] if k[31] != None else 0
			k[32] = k[31]/k[30] if k[30] != 0 else 0
		list_total.append(total_amt)
		total_amt = 0
		for k in data:
			total_amt += k[28] if k[28] != None else 0
		list_total.append(total_amt)
		list_total.append('100')
		for k in data:
			qty += k[30] if k[30] != None else 0
			k[34] = k[34] if k[34] != None else 0
			k[35] = k[35] if k[35] != None else 0
			k[36] = k[35]/k[34] if k[34] != 0 else 0
		list_total.append(qty)
		qty = 0
		for k in data:	
			qty += k[31] if k[31] != None else 0
		list_total.append(qty)
		total_amt = 0
		for k in data:
			total_amt += k[32] if k[32] != None else 0
		list_total.append(total_amt)
		list_total.append('100')
		amt = 0
		for k in data:
			amt += k[34] if k[34] != None else 0
		list_total.append(amt)
		total_qty = 0
		for k in data:
			total_qty += k[35] if k[35] != None else 0
		list_total.append(total_qty)
		total_amt = 0
		for k in data:
			total_amt += k[36] if k[36] != None else 0
			k[38] = k[38] if k[38] != None else 0
			k[39] = k[39] if k[39] != None else 0
			k[40] = k[39]/k[38] if k[38] != 0 else 0
		list_total.append(total_amt)
		list_total.append('100')
		total_amt = 0
		for k in data:
			total_amt += k[38] if k[38] != None else 0
		list_total.append(total_amt)
		qty = 0
		for k in data:
			qty += k[39] if k[39] != None else 0
			k[42] = k[42] if k[42] != None else 0
			k[43] = k[43] if k[43] != None else 0
			k[44] = k[43]/k[42] if k[42] != 0 else 0
		list_total.append(qty)
		total_amt = 0
		for k in data:
			total_amt += k[40] if k[40] != None else 0
		list_total.append(total_amt)
		list_total.append('100')
		for k in data:
			total_amt += k[42] if k[42] != None else 0
		list_total.append(total_amt)
		for k in data:
			qty += k[43] if k[43] != None else 0
			k[46] = k[46] if k[46] != None else 0
			k[47] = k[47] if k[47] != None else 0
			k[48] = k[47]/k[46] if k[46] != 0 else 0
		list_total.append(qty)
		total_amt = 0
		for k in data:
			total_amt += k[44] if k[44] != None else 0
		list_total.append(total_amt)
		list_total.append('100')
		qty = 0
		for k in data:	
			qty += k[46] if k[46] != None else 0
		list_total.append(qty)
		amt = 0
		for k in data:
			amt += k[47] if k[47] != None else 0
		list_total.append(amt)
		total_amt = 0
		for k in data:
			total_amt += k[48] if k[48] != None else 0
		list_total.append(total_amt)
		list_total.append('100')
		total_qty = 0
		for k in data:
			total_qty += k[50] if k[50] != None else 0
		list_total.append(total_qty)
		total_amt = 0
		for k in data:
			total_amt += k[51] if k[51] != None else 0
		list_total.append(total_amt)
		for i in data:
			jan += i[3] if i[3] != None else 0
			feb += i[7] if i[7] != None else 0
			mar += i[11] if i[11] != None else 0
			apr += i[15] if i[15] != None else 0
			may += i[19] if i[19] != None else 0
			jun += i[23] if i[23] != None else 0
			july += i[27] if i[27] != None else 0
			aug += i[31] if i[31] != None else 0
			sep += i[35] if i[35] != None else 0
			oct += i[39] if i[39] != None else 0
			nov += i[43] if i[43] != None else 0
			dec += i[47] if i[47] != None else 0
		for j in data:
			print(j[3])
			print(jan)
			j[5] = '{:.2f}%'.format((j[3]/jan)*100) if j[3] != 0 else 0
			j[9] = '{:.2f}%'.format((j[7]/feb)*100) if j[7] != 0 else 0
			j[13] = '{:.2f}%'.format((j[11]/mar)*100) if j[11] != 0 else 0
			j[17] = '{:.2f}%'.format((j[15]/apr)*100) if j[15] != 0 else 0
			j[21] = '{:.2f}%'.format((j[19]/may)*100) if j[19] != 0 else 0
			j[25] = '{:.2f}%'.format((j[23]/jun)*100) if j[23] != 0 else 0
			j[29] = '{:.2f}%'.format((j[27]/july)*100) if j[27] != 0 else 0
			j[33] = '{:.2f}%'.format((j[31]/aug)*100) if j[31] != 0 else 0
			j[37] = '{:.2f}%'.format((j[35]/sep)*100) if j[35] != 0 else 0
			j[41] = '{:.2f}%'.format((j[39]/oct)*100) if j[39] != 0 else 0
			j[45] = '{:.2f}%'.format((j[43]/nov)*100) if j[43] != 0 else 0
			j[49] = '{:.2f}%'.format((j[47]/dec)*100) if j[47] != 0 else 0
	data.append(list_total)
	return data

def get_mon(dt):
	return getdate(dt).strftime("%b")

def period_wise_columns_query(filters, trans):
	query_details = ''
	pwc = []
	bet_dates = get_period_date_ranges(filters.get("period"), filters.get("fiscal_year"))

	if trans in ['Purchase Receipt', 'Delivery Note', 'Purchase Invoice', 'Sales Invoice']:
		trans_date = 'posting_date'
		if filters.period_based_on:
			trans_date = filters.period_based_on
	else:
		trans_date = 'transaction_date'

	if filters.get("period") != 'Yearly':
		for dt in bet_dates:
			get_period_wise_columns(dt, filters.get("period"), pwc)
			query_details = get_period_wise_query(dt, trans_date, query_details)
	else:
		pwc = [_(filters.get("fiscal_year")) + " ("+_("Qty in KG") + "):Float:120",
			_(filters.get("fiscal_year")) + " ("+ _("Amt") + "):Currency:120",
			_(filters.get("fiscal_year")) + " ("+_("Rate per KG") + "):Float:120",
			_(filters.get("fiscal_year")) + " ("+ _("Percentage") + "):Percent:120",]
		query_details = " SUM(t2.total_net_weight), SUM(t2.amount), NULL, NULL,"

	query_details += 'SUM(t2.total_net_weight), SUM(t2.amount), NULL, NULL'
	return pwc, query_details

def get_period_wise_columns(bet_dates, period, pwc):
	if period == 'Monthly':
		pwc += [_(get_mon(bet_dates[0])) + " (" + _("Qty in KG") + "):Float:120",
			_(get_mon(bet_dates[0])) + " (" + _("Amt") + "):Currency:120",
			_(get_mon(bet_dates[0])) + " (" + _("Rate per KG") + "):Float:120",
			_(get_mon(bet_dates[0])) + " (" + _("Percentage") + "):Percent:120"]
	else:
		pwc += [_(get_mon(bet_dates[0])) + "-" + _(get_mon(bet_dates[1])) + " (" + _("Qty in KG") + "):Float:120",
			_(get_mon(bet_dates[0])) + "-" + _(get_mon(bet_dates[1])) + " (" + _("Amt") + "):Currency:120",
			_(get_mon(bet_dates[0])) + "-" + _(get_mon(bet_dates[1])) + " (" + _("Rate per KG") + "):Float:120",
			_(get_mon(bet_dates[0])) + "-" + _(get_mon(bet_dates[1])) + " (" + _("Percentage") + "):Percent:120"]

def get_period_wise_query(bet_dates, trans_date, query_details):
	query_details += """SUM(IF(t1.%(trans_date)s BETWEEN '%(sd)s' AND '%(ed)s', t2.total_net_weight, NULL)),
					SUM(IF(t1.%(trans_date)s BETWEEN '%(sd)s' AND '%(ed)s', t2.amount, NULL)),
					NULL,
					NULL,
				""" % {"trans_date": trans_date, "sd": bet_dates[0],"ed": bet_dates[1]}
	return query_details

@frappe.whitelist(allow_guest=True)
def get_period_date_ranges(period, fiscal_year=None, year_start_date=None):
	from dateutil.relativedelta import relativedelta

	if not year_start_date:
		year_start_date, year_end_date = frappe.db.get_value("Fiscal Year",
			fiscal_year, ["year_start_date", "year_end_date"])

	increment = {
		"Monthly": 1,
		"Quarterly": 3,
		"Half-Yearly": 6,
		"Yearly": 12
	}.get(period)

	period_date_ranges = []
	for i in range(1, 13, increment):
		period_end_date = getdate(year_start_date) + relativedelta(months=increment, days=-1)
		if period_end_date > getdate(year_end_date):
			period_end_date = year_end_date
		period_date_ranges.append([year_start_date, period_end_date])
		year_start_date = period_end_date + relativedelta(days=1)
		if period_end_date == year_end_date:
			break

	return period_date_ranges

def get_period_month_ranges(period, fiscal_year):
	from dateutil.relativedelta import relativedelta
	period_month_ranges = []

	for start_date, end_date in get_period_date_ranges(period, fiscal_year):
		months_in_this_period = []
		while start_date <= end_date:
			months_in_this_period.append(start_date.strftime("%B"))
			start_date += relativedelta(months=1)
		period_month_ranges.append(months_in_this_period)

	return period_month_ranges

def based_wise_columns_query(based_on, trans):
	based_on_details = {}

	# based_on_cols, based_on_select, based_on_group_by, addl_tables
	if based_on == "Item":
		based_on_details["based_on_cols"] = ["Item:Link/Item:120", "Item Name:Data:120"]
		based_on_details["based_on_select"] = "t2.item_code, t2.item_name,"
		based_on_details["based_on_group_by"] = 't2.item_code'
		based_on_details["addl_tables"] = ''

	elif based_on == "Item Group":
		based_on_details["based_on_cols"] = ["Item Group:Link/Item Group:120"]
		based_on_details["based_on_select"] = "t2.item_group,"
		based_on_details["based_on_group_by"] = 't2.item_group'
		based_on_details["addl_tables"] = ''

	elif based_on == "Customer":
		based_on_details["based_on_cols"] = ["Customer:Link/Customer:120", "Territory:Link/Territory:120"]
		based_on_details["based_on_select"] = "t1.customer_name, t1.territory, "
		based_on_details["based_on_group_by"] = 't1.party_name' if trans == 'Quotation' else 't1.customer'
		based_on_details["addl_tables"] = ''

	elif based_on == "Customer Group":
		based_on_details["based_on_cols"] = ["Customer Group:Link/Customer Group"]
		based_on_details["based_on_select"] = "t1.customer_group,"
		based_on_details["based_on_group_by"] = 't1.customer_group'
		based_on_details["addl_tables"] = ''

	elif based_on == 'Supplier':
		based_on_details["based_on_cols"] = ["Supplier:Link/Supplier:120", "Supplier Group:Link/Supplier Group:140"]
		based_on_details["based_on_select"] = "t1.supplier, t3.supplier_group,"
		based_on_details["based_on_group_by"] = 't1.supplier'
		based_on_details["addl_tables"] = ',`tabSupplier` t3'
		based_on_details["addl_tables_relational_cond"] = " and t1.supplier = t3.name"

	elif based_on == 'Supplier Group':
		based_on_details["based_on_cols"] = ["Supplier Group:Link/Supplier Group:140"]
		based_on_details["based_on_select"] = "t3.supplier_group,"
		based_on_details["based_on_group_by"] = 't3.supplier_group'
		based_on_details["addl_tables"] = ',`tabSupplier` t3'
		based_on_details["addl_tables_relational_cond"] = " and t1.supplier = t3.name"

	elif based_on == "Territory":
		based_on_details["based_on_cols"] = ["Territory:Link/Territory:120"]
		based_on_details["based_on_select"] = "t1.territory,"
		based_on_details["based_on_group_by"] = 't1.territory'
		based_on_details["addl_tables"] = ''

	elif based_on == "Project":
		if trans in ['Sales Invoice', 'Delivery Note', 'Sales Order']:
			based_on_details["based_on_cols"] = ["Project:Link/Project:120"]
			based_on_details["based_on_select"] = "t1.project,"
			based_on_details["based_on_group_by"] = 't1.project'
			based_on_details["addl_tables"] = ''
		elif trans in ['Purchase Order', 'Purchase Invoice', 'Purchase Receipt']:
			based_on_details["based_on_cols"] = ["Project:Link/Project:120"]
			based_on_details["based_on_select"] = "t2.project,"
			based_on_details["based_on_group_by"] = 't2.project'
			based_on_details["addl_tables"] = ''
		else:
			frappe.throw(_("Project-wise data is not available for Quotation"))

	return based_on_details

def group_wise_column(group_by):
	if group_by:
		return [group_by+":Link/"+group_by+":120"]
	else:
		return []
