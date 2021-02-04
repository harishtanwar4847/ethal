# -*- coding: utf-8 -*-
# Copyright (c) 2021, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime

class MeltingFurnace(Document):
	def after_insert(self):
		if self.date:
			my_date = datetime.strptime(self.date, '%Y-%m-%d')
			day =my_date.strftime('%A')
			month = my_date.strftime('%B')
			self.day = day
			self.month = month
		print(self.melting_furnace_items)
		for i in self.melting_furnace_items:
			i.shift_a_in_kg = float(i.rolling_ingot_weight) * i.shift_a_in_nos if i.rolling_ingot_weight and i.shift_a_in_nos else 0
			i.shift_b_in_kg = float(i.rolling_ingot_weight) * i.shift_b_in_nos if i.rolling_ingot_weight and i.shift_b_in_nos else 0
			i.shift_c_in_kg = float(i.rolling_ingot_weight) * i.shift_c_in_nos if i.rolling_ingot_weight and i.shift_c_in_nos else 0
			i.total_pieces = i.shift_a_in_nos + i.shift_b_in_nos + i.shift_c_in_nos  
			i.total_weight = i.total_pieces * float(i.rolling_ingot_weight)
			i.heats = i.total_pieces/float(i.no_of_ingots_per_heat) if i.no_of_ingots_per_heat else 0
			i.save(ignore_permissions=True)
		# frappe.throw('ja na be')

	def before_save(self):
		if self.date:
			print(self.date)
			my_date = datetime.strptime(self.date, '%Y-%m-%d')
			day =my_date.strftime('%A')
			month = my_date.strftime('%B')
			self.day = day
			self.month = month
		for i in self.melting_furnace_items:
			i.shift_a_in_kg = float(i.rolling_ingot_weight) * i.shift_a_in_nos if i.rolling_ingot_weight and i.shift_a_in_nos else 0
			i.shift_b_in_kg = float(i.rolling_ingot_weight) * i.shift_b_in_nos if i.rolling_ingot_weight and i.shift_b_in_nos else 0
			i.shift_c_in_kg = float(i.rolling_ingot_weight) * i.shift_c_in_nos if i.rolling_ingot_weight and i.shift_c_in_nos else 0
			i.total_pieces = i.shift_a_in_nos + i.shift_b_in_nos + i.shift_c_in_nos  
			i.total_weight = i.total_pieces * float(i.rolling_ingot_weight)
			i.heats = i.total_pieces/float(i.no_of_ingots_per_heat) if i.no_of_ingots_per_heat else 0

