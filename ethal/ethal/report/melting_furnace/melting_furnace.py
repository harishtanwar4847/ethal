# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	columns = ["Melting Furnace:Link/Melting Furnace:200"]+["MF:Data:100"]+["Rolling Ingot Weight:Float:100"]+["No of Ingots per heat:int:100"]+["Shift A - In Nos:Int:100"]+["Shift A - In Kg:Float:100"]+["Shift B - In Nos:Int:100"]+["Shift B - In Kg:Float:100"]+["Shift C - In Nos:Int:100"]+["Shift C - In Kg:Float:100"]+["Total Pieces:Int:100"]+["Total Weight:Float:100"]+["Heats:Int:100"]
	data = get_date(filters)
	return columns, data

def get_date(filters):
	if filters.melting_furnace:
		return frappe.db.sql("""
			select parent, mf, cast(rolling_ingot_weight as decimal(10,6)), cast(no_of_ingots_per_heat as int), shift_a_in_nos, shift_a_in_kg, 
				shift_b_in_nos, shift_b_in_kg, shift_c_in_nos, shift_c_in_kg, total_pieces, total_weight, heats
			from `tabMelting Furnace Items`	
			where parent = '{0}'	
			order by parent	
		""".format(filters.melting_furnace))
	else:
		return frappe.db.sql("""
			select parent, mf, cast(rolling_ingot_weight as decimal(10,6)), cast(no_of_ingots_per_heat as int), shift_a_in_nos, shift_a_in_kg, 
				shift_b_in_nos, shift_b_in_kg, shift_c_in_nos, shift_c_in_kg, total_pieces, total_weight, heats
			from `tabMelting Furnace Items`	
			order by parent	
		""")	

