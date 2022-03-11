# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate

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
							data1[d][0]), as_list=1, debug=1)

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
				(filters.get("company"), year_start_date, year_end_date), as_list=1, debug=1)

	str = 'Total'
	total = 	"\033[1m" + str + "\033[0m"
	list_total = ['Total', '']		
	if filters.get("period") == 'Yearly':
		year = 0
		qty = 0
		qty_kg = 0
		for k in data:
			qty_kg += k[2] if k[2] != None else 0
		list_total.append(qty_kg)
		for k in data:
			qty += k[3] if k[3] != None else 0
		list_total.append(qty)
		amt = 0
		for k in data:
			amt += k[4] if k[4] != None else 0
		list_total.append(amt)
		rate = 0
		for j in data:
			rate += j[5] if j[5] != None else 0
		list_total.append(rate)	
		list_total.append('100')
		total_qty = 0
		for k in data:
			total_qty += k[7] if k[7] != None else 0
		list_total.append(total_qty)
		total_amt = 0
		for k in data:
			total_amt += k[8] if k[8] != None else 0
		list_total.append(total_amt)
		for i in data:
			year += i[4]	
		for j in data:
			j[6] = '{:.2f}%'.format((j[4]/year)*100)
	elif filters.get("period") == 'Half-Yearly':
		jan_jun, jul_dec = 0, 0
		jan_jun_qty = 0
		for k in data:	
			jan_jun_qty += k[2] if k[2] != None else 0
		list_total.append(jan_jun_qty)
		jan_jun_qty_kg = 0
		for k in data:	
			jan_jun_qty_kg += k[3] if k[3] != None else 0
		list_total.append(jan_jun_qty_kg)
		amt = 0
		for k in data:
			amt += k[4] if k[4] != None else 0
		list_total.append(amt)
		rate = 0
		for k in data:
			rate += k[5] if k[5] != None else 0
		list_total.append(rate)
		list_total.append('100')
		jul_dec_qty = 0
		for k in data:
			jul_dec_qty += k[7] if k[7] != None else 0
		list_total.append(jul_dec_qty)
		jul_dec_kg = 0
		for k in data:
			jul_dec_kg += k[8] if k[8] != None else 0
		list_total.append(jul_dec_kg)
		total_amt = 0
		for k in data:
			total_amt += k[9] if k[9] != None else 0
		list_total.append(total_amt)
		total_rate = 0
		for k in data:
			total_rate += k[10] if k[10] != None else 0
		list_total.append(total_rate)
		list_total.append('100')
		total_qty = 0
		for k in data:
			total_qty += k[12] if k[12] != None else 0
		list_total.append(total_qty)
		amt = 0
		for k in data:
			amt += k[13] if k[13] != None else 0
		list_total.append(amt)
		for i in data:
			jan_jun += i[4]	if i[4] != None else 0
			jul_dec += i[9]	if i[9] != None else 0	
		for j in data:
			j[6] = '{:.2f}%'.format((j[4]/jan_jun)*100) if j[4] != 0 else 0
			j[11] = '{:.2f}%'.format((j[9]/jul_dec)*100) if j[9] != None else 0 		
	elif filters.get("period") == 'Quarterly':
		jan_mar, apr_jun, jul_sep, oct_dec = 0, 0, 0, 0
		jan_mar_qty = 0
		for k in data:	
			jan_mar_qty += k[2] if k[2] != None else 0
		list_total.append(jan_mar_qty)
		jan_mar_qty_kg = 0
		for k in data:	
			jan_mar_qty_kg += k[3] if k[3] != None else 0
		list_total.append(jan_mar_qty_kg)
		amt = 0
		for k in data:
			amt += k[4] if k[4] != None else 0
		list_total.append(amt)
		total_rate = 0
		for k in data:
			total_rate += k[5] if k[5] != None else 0
		list_total.append(total_rate)
		list_total.append('100')
		apr_jun_qty = 0
		for k in data:
			apr_jun_qty += k[7] if k[7] != None else 0
		list_total.append(apr_jun_qty)
		apr_jun_qty_kg = 0
		for k in data:
			apr_jun_qty_kg += k[8] if k[8] != None else 0
		list_total.append(apr_jun_qty_kg)
		total_amt = 0
		for k in data:
			total_amt += k[9] if k[9] != None else 0
		list_total.append(total_amt)
		total_amt = 0
		for k in data:
			total_amt += k[10] if k[10] != None else 0
		list_total.append(total_amt)
		list_total.append('100')
		jul_sep_qty = 0
		for k in data:
			jul_sep_qty += k[12] if k[12] != None else 0
		list_total.append(jul_sep_qty)
		jul_sep_qty_kg = 0
		for k in data:	
			jul_sep_qty_kg += k[13] if k[13] != None else 0
		list_total.append(jul_sep_qty_kg)
		qty_kg = 0
		for k in data:	
			qty_kg += k[14] if k[14] != None else 0
		list_total.append(qty_kg)
		total_amt = 0
		for k in data:
			total_amt += k[15] if k[15] != None else 0
		list_total.append(total_amt)
		list_total.append('100')
		oct_dec_qty = 0
		for k in data:
			oct_dec_qty += k[17] if k[17] != None else 0
		list_total.append(oct_dec_qty)
		oct_dec_qty_kg = 0
		for k in data:
			oct_dec_qty_kg += k[18] if k[18] != None else 0
		list_total.append(oct_dec_qty_kg)
		amt = 0
		for k in data:
			amt += k[19] if k[19] != None else 0
		list_total.append(amt)
		rate = 0
		for k in data:
			rate += k[20] if k[20] != None else 0
		list_total.append(rate)
		list_total.append('100')
		total_qty = 0
		for k in data:
			total_qty += k[22] if k[22] != None else 0
		list_total.append(total_qty)
		total_amt = 0
		for k in data:
			total_amt += k[23] if k[23] != None else 0
		list_total.append(total_amt)
		for i in data:
			jan_mar += i[4] if i[4] != None else 0
			apr_jun += i[9] if i[9] != None else 0
			jul_sep += i[14] if i[14] != None else 0 		
			oct_dec += i[19] if i[19] != None else 0
		for j in data:
			j[6] =  '{:.2f}%'.format((j[4]/jan_mar)*100) if j[4] != None else 0
			j[11] =  '{:.2f}%'.format((j[9]/apr_jun)*100)  if j[9] != None else 0
			j[16] =  '{:.2f}%'.format((j[14]/jul_sep)*100) if j[14] != None else 0
			j[21] =  '{:.2f}%'.format((j[19]/oct_dec)*100) if j[19] != None else 0	
	elif filters.get("period") == 'Monthly':		
		jan , feb , mar, apr, may, jun, july, aug, sep, oct, nov, dec = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
		jan_qty = 0
		for k in data:	
			jan_qty += k[2] if k[2] != None else 0
		list_total.append(jan_qty)
		jan_qty_kg = 0
		for k in data:	
			jan_qty_kg += k[3] if k[3] != None else 0
		list_total.append(jan_qty_kg)
		amt = 0
		for k in data:
			amt += k[4] if k[4] != None else 0
		list_total.append(amt)
		rate = 0
		for k in data:
			rate += k[5] if k[5] != None else 0
		list_total.append(rate)
		list_total.append('100')
		feb_qty = 0
		for k in data:
			feb_qty += k[7] if k[7] != None else 0
		list_total.append(feb_qty)
		feb_qty_kg = 0
		for k in data:
			feb_qty_kg += k[8] if k[8] != None else 0
		list_total.append(feb_qty_kg)
		amt = 0
		for k in data:
			amt += k[9] if k[9] != None else 0
		list_total.append(amt)
		rate = 0
		for k in data:
			rate += k[10] if k[10] != None else 0
		list_total.append(rate)
		list_total.append('100')
		mar_qty = 0
		for k in data:
			mar_qty += k[12] if k[12] != None else 0
		list_total.append(mar_qty)
		mar_qty_kg = 0
		for k in data:
			mar_qty_kg += k[13] if k[13] != None else 0
		list_total.append(mar_qty_kg)
		amt = 0
		for k in data:	
			amt += k[14] if k[14] != None else 0
		list_total.append(amt)
		rate = 0
		for k in data:
			rate += k[15] if k[15] != None else 0
		list_total.append(rate)
		list_total.append('100')
		apr_qty = 0
		for k in data:
			apr_qty += k[17] if k[17] != None else 0
		list_total.append(apr_qty)
		apr_qty_kg = 0
		for k in data:
			apr_qty_kg += k[18] if k[18] != None else 0
		list_total.append(apr_qty_kg)
		amt = 0
		for k in data:
			amt += k[19] if k[19] != None else 0
		list_total.append(amt)
		rate = 0
		for k in data:
			rate += k[20] if k[20] != None else 0
		list_total.append(rate)
		list_total.append('100')
		may_qty = 0
		for k in data:
			may_qty += k[22] if k[22] != None else 0
		list_total.append(may_qty)
		may_qty_kg = 0
		for k in data:
			may_qty_kg += k[23] if k[23] != None else 0
		list_total.append(may_qty_kg)
		amt = 0
		for k in data:
			amt += k[24] if k[24] != None else 0
		list_total.append(amt)
		rate = 0
		for k in data:
			rate += k[25] if k[25] != None else 0
		list_total.append(rate)
		list_total.append('100')
		jun_qty = 0
		for k in data:
			jun_qty += k[27] if k[27] != None else 0
		list_total.append(jun_qty)
		jun_qty_kg = 0
		for k in data:
			jun_qty_kg += k[28] if k[28] != None else 0
		list_total.append(jun_qty_kg)
		amt = 0
		for k in data:
			amt += k[29] if k[29] != None else 0
		list_total.append(amt)
		rate = 0
		for k in data:
			rate += k[30] if k[30] != None else 0
		list_total.append(rate)
		list_total.append('100')
		jul_qty = 0
		for k in data:
			jul_qty += k[32] if k[32] != None else 0
		list_total.append(jul_qty)
		jul_qty_kg = 0
		for k in data:
			jul_qty_kg += k[33] if k[33] != None else 0
		list_total.append(jul_qty_kg)
		amt = 0
		for k in data:
			amt += k[34] if k[34] != None else 0
		list_total.append(amt)
		rate = 0
		for k in data:
			rate += k[35] if k[35] != None else 0
		list_total.append(rate)
		list_total.append('100')
		aug_qty = 0
		for k in data:
			aug_qty += k[37] if k[37] != None else 0
		list_total.append(aug_qty)
		aug_qty_kg = 0
		for k in data:
			aug_qty_kg += k[38] if k[38] != None else 0
		list_total.append(aug_qty_kg)
		amt = 0
		for k in data:
			amt += k[39] if k[39] != None else 0
		list_total.append(amt)
		rate = 0
		for k in data:
			rate += k[40] if k[40] != None else 0
		list_total.append(rate)	
		list_total.append('100')
		sep_qty = 0
		for k in data:
			sep_qty += k[42] if k[42] != None else 0
		list_total.append(sep_qty)
		sep_qty_kg = 0
		for k in data:
			sep_qty_kg += k[43] if k[43] != None else 0
		list_total.append(sep_qty_kg)
		amt = 0
		for k in data:
			amt += k[44] if k[44] != None else 0
		list_total.append(amt)
		rate = 0
		for k in data:
			rate += k[45] if k[45] != None else 0
		list_total.append(rate)	
		list_total.append('100')
		oct_qty = 0
		for k in data:
			oct_qty += k[47] if k[47] != None else 0
		list_total.append(oct_qty)
		oct_qty_kg = 0
		for k in data:
			oct_qty_kg += k[48] if k[48] != None else 0
		list_total.append(oct_qty_kg)
		amt = 0
		for k in data:
			amt += k[49] if k[49] != None else 0
		list_total.append(amt)
		rate = 0
		for k in data:
			rate += k[50] if k[50] != None else 0
		list_total.append(rate)	
		list_total.append('100')
		nov_qty = 0
		for k in data:
			nov_qty += k[52] if k[52] != None else 0
		list_total.append(nov_qty)
		nov_qty_kg = 0
		for k in data:
			nov_qty_kg += k[53] if k[53] != None else 0
		list_total.append(nov_qty_kg)
		amt = 0
		for k in data:
			amt += k[54] if k[54] != None else 0
		list_total.append(amt)
		rate = 0
		for k in data:
			rate += k[55] if k[55] != None else 0
		list_total.append(rate)	
		list_total.append('100')
		dec_qty = 0
		for k in data:
			dec_qty += k[57] if k[57] != None else 0
		list_total.append(dec_qty)
		dec_qty_kg = 0
		for k in data:
			dec_qty_kg += k[58] if k[58] != None else 0
		list_total.append(dec_qty_kg)
		amt = 0
		for k in data:
			amt += k[59] if k[59] != None else 0
		list_total.append(amt)
		rate = 0
		for k in data:
			rate += k[60] if k[60] != None else 0
		list_total.append(rate)	
		list_total.append('100')
		total_qty = 0
		for k in data:
			total_qty += k[62] if k[62] != None else 0
		list_total.append(total_qty)
		total_amt = 0
		for k in data:
			total_amt += k[63] if k[63] != None else 0
		list_total.append(total_amt)
		for i in data:
			jan += i[4] if i[4] != None else 0
			feb += i[9] if i[9] != None else 0
			mar += i[14] if i[14] != None else 0
			apr += i[19] if i[19] != None else 0
			may += i[24] if i[24] != None else 0
			jun += i[29] if i[29] != None else 0
			july += i[34] if i[34] != None else 0
			aug += i[39] if i[39] != None else 0
			sep += i[44] if i[44] != None else 0
			oct += i[49] if i[49] != None else 0
			nov += i[54] if i[54] != None else 0
			dec += i[59] if i[59] != None else 0
		for j in data:
			j[6] = '{:.2f}%'.format((j[4]/jan)*100) if j[4] != None else 0
			j[11] = '{:.2f}%'.format((j[9]/feb)*100) if j[9] != None else 0
			j[16] = '{:.2f}%'.format((j[14]/mar)*100) if j[14] != None else 0
			j[21] = '{:.2f}%'.format((j[19]/apr)*100) if j[19] != None else 0
			j[26] = '{:.2f}%'.format((j[24]/may)*100) if j[24] != None else 0
			j[31] = '{:.2f}%'.format((j[29]/jun)*100) if j[29] != None else 0
			j[36] = '{:.2f}%'.format((j[34]/july)*100) if j[34] != None else 0
			j[41] = '{:.2f}%'.format((j[39]/aug)*100) if j[39] != None else 0
			j[46] = '{:.2f}%'.format((j[44]/sep)*100) if j[44] != None else 0
			j[51] = '{:.2f}%'.format((j[49]/oct)*100) if j[49] != None else 0
			j[56] = '{:.2f}%'.format((j[54]/nov)*100) if j[54] != None else 0
			j[61] = '{:.2f}%'.format((j[59]/dec)*100) if j[59] != None else 0

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
		pwc = [_(filters.get("fiscal_year")) + " ("+_("Qty") + "):Float:120",
			_(filters.get("fiscal_year")) + " ("+_("Qty in KG") + "):Float:150",
			_(filters.get("fiscal_year")) + " ("+ _("Amt") + "):Currency:120",
			_(filters.get("fiscal_year")) + " ("+ _("Rate per KG") + "):Float:180",
			_(filters.get("fiscal_year")) + " ("+ _("Percentage") + "):Percent:180",]
		query_details = " SUM(t2.stock_qty), SUM(t2.total_net_weight), SUM(t2.base_net_amount), SUM(t2.base_net_amount) / SUM(t2.stock_qty), Null,"
		
	query_details += 'SUM(t2.stock_qty), SUM(t2.base_net_amount)'
	
	return pwc, query_details

def get_period_wise_columns(bet_dates, period, pwc):
	if period == 'Monthly':
		pwc += [_(get_mon(bet_dates[0])) + " (" + _("Qty") + "):Float:120",
			_(get_mon(bet_dates[0])) + " (" + _("Qty in KG") + "):Float:150",
			_(get_mon(bet_dates[0])) + " (" + _("Amt") + "):Currency:120",
			_(get_mon(bet_dates[0])) + " (" + _("Rate per KG") + "):Float:180",
			_(get_mon(bet_dates[0])) + " (" + _("Percentage") + "):Percent:180"]
	else:
		pwc += [_(get_mon(bet_dates[0])) + "-" + _(get_mon(bet_dates[1])) + " (" + _("Qty") + "):Float:120",
			_(get_mon(bet_dates[0])) + "-" + _(get_mon(bet_dates[1])) + " (" + _("Qty in KG") + "):Float:150",
			_(get_mon(bet_dates[0])) + "-" + _(get_mon(bet_dates[1])) + " (" + _("Amt") + "):Currency:120",
			_(get_mon(bet_dates[0])) + "-" + _(get_mon(bet_dates[1])) + " (" + _("Rate per KG") + "):Float:180",
			_(get_mon(bet_dates[0])) + "-" + _(get_mon(bet_dates[1])) + " (" + _("Percentage") + "):Percent:180"]

def get_period_wise_query(bet_dates, trans_date, query_details):
	query_details += """SUM(IF(t1.%(trans_date)s BETWEEN '%(sd)s' AND '%(ed)s', t2.stock_qty, NULL)),
					SUM(IF(t1.%(trans_date)s BETWEEN '%(sd)s' AND '%(ed)s', t2.total_net_weight, NULL)),
					SUM(IF(t1.%(trans_date)s BETWEEN '%(sd)s' AND '%(ed)s', t2.base_net_amount, NULL)),
					SUM(IF(t1.%(trans_date)s BETWEEN '%(sd)s' AND '%(ed)s', t2.base_net_amount/t2.stock_qty, NULL)), 
					Null,
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
