# Copyright (c) 2022, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, cstr, date_diff, flt, formatdate, getdate, now_datetime, nowdate
from datetime import timedelta, datetime

class FSNumberPeriod(Document):
	def validate(self):
		self.validate_overlapping_dates()

		if self.end_date and self.end_date <= self.start_date:
			frappe.throw(_("End Date must not be lesser than Start Date"))

	def validate_overlapping_dates(self):
		if not self.name:
			self.name = "New FS Number Period"

		condition = """and (
				end_date is null
				or
					%(start_date)s between start_date and end_date
		"""

		if self.end_date:
			condition  += """ or
					%(end_date)s between start_date and end_date
					or
					start_date between %(start_date)s and %(end_date)s
				) """
		else:
			condition += """ ) """

		assigned_shifts = frappe.db.sql("""
			select name, series, start_date ,end_date, docstatus, status
			from `tabFS Number Period`
			where
				series=%(series)s and docstatus = 1
				and name != %(name)s
				and status = "Active"
				{0}
		""".format(condition), {
			"series": self.series,
			"start_date": self.start_date,
			"end_date": self.end_date,
			"name": self.name
		}, as_dict = 1)

		if len(assigned_shifts):
			self.throw_overlap_error(assigned_shifts[0])

	def throw_overlap_error(self, shift_details):
		shift_details = frappe._dict(shift_details)
		if shift_details.docstatus == 1 and shift_details.status == "Active":
			msg = _("Series {0} already has Active Period {1}").format(frappe.bold(self.series), frappe.bold(shift_details.name))
		if shift_details.start_date:
			msg += _(" from {0}").format(getdate(self.start_date).strftime("%d-%m-%Y"))
			title = "Ongoing Shift"
			if shift_details.end_date:
				msg += _(" to {0}").format(getdate(self.end_date).strftime("%d-%m-%Y"))
				title = "Active Shift"
		if msg:
			frappe.throw(msg, title=title)	