# -*- coding: utf-8 -*-
# Copyright (c) 2020, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class EmployeeIncentiveBulk(Document):
	def on_submit(self):
		employees = frappe.db.get_all('Employee Incentive Bulk Detail', {'parent': self.name}, ['employee', 'incentive_hours'], as_list = 1)
		if employees:
			for employee in employees:
					company = frappe.db.get_value('Employee', employee[0], 'company')
					additional_salary = frappe.db.exists('Additional Salary', {
							'employee': employee[0], 
							'salary_component': self.salary_component,
							'payroll_date': self.incentive_date, 
							'company': company,
							'docstatus': 1
						})
					incentive_amount = 0
					if not additional_salary:
						print('in if condition')
						additional_salary = frappe.new_doc('Additional Salary')
						additional_salary.employee = employee[0]
						additional_salary.salary_component = self.salary_component
						base_value = frappe.get_value('Salary Structure Assignment', {'employee': employee[0], 'docstatus': 1}, 'base')
						print(base_value)
						if base_value:
							incentive_amount = (base_value / 26 / 8) * employee[1]
							additional_salary.amount = incentive_amount
						else:
							additional_salary.amount = 0	
						additional_salary.payroll_date = self.incentive_date
						additional_salary.company = company
						additional_salary.submit()
						# self.db_set('additional_salary', additional_salary.name)

					else:
						incentive_added = frappe.db.get_value('Additional Salary', additional_salary, 'amount') + incentive_amount
						frappe.db.set_value('Additional Salary', additional_salary, 'amount', incentive_added)
						# self.db_set('additional_salary', additional_salary)

	def on_cancel(self):
		incentives = frappe.db.get_all('Additional Salary', {'payroll_date': self.incentive_date}, ['name', 'amount'], as_list=1)
		print(incentives)
		if incentives:
			for i in incentives:
				incentive_removed = frappe.db.get_value('Additional Salary', i[0], 'amount') - i[1]
				if incentive_removed == 0:
					frappe.get_doc('Additional Salary', i[0]).cancel()
					frappe.db.commit()
				else:
					frappe.db.set_value('Additional Salary', i[0], 'amount', incentive_removed)
					frappe.db.commit()

	def get_emp_list(self):
		"""
			Returns list of active employees based on selected criteria
			and for which salary structure exists
		"""

		cond = self.get_filter_condition()
		# cond += self.get_joining_relieving_condition()
		if cond:
			emp_list = frappe.db.sql("""
				select
					distinct t1.name as employee, t1.employee_name, t1.department, t1.designation
				from
					`tabEmployee` t1
				where %s
			""" % cond,  as_dict=True)
			print(emp_list)
		else:
			emp_list = frappe.db.sql("""
				select
					distinct t1.name as employee, t1.employee_name, t1.department, t1.designation
				from
					`tabEmployee` t1
			""",  as_dict=True)
			print(emp_list)	
		return emp_list

	def fill_employee_details(self):
		self.set('employee_details', [])
		employees = self.get_emp_list()
		if not employees:
			frappe.throw(_("No employees for the mentioned criteria"))
			
		for d in employees:
			self.append('employee_details', d)

		self.number_of_employees = len(employees)
		# if self.validate_attendance:
		# return self.validate_employee_attendance()

	def get_filter_condition(self):
		# self.check_mandatory()

		cond = ''
		for f in ['company', 'branch', 'department', 'designation']:
			if self.get(f):
				cond += " t1." + f + " = '" + self.get(f).replace("'", "\'") + "'"

		return cond

	def get_joining_relieving_condition(self):
		cond = """
			and ifnull(t1.date_of_joining, '0000-00-00') <= '%(end_date)s'
			and ifnull(t1.relieving_date, '2199-12-31') >= '%(start_date)s'
		""" % {"start_date": self.start_date, "end_date": self.end_date}
		return cond

	def check_mandatory(self):
		for fieldname in ['company', 'start_date', 'end_date']:
			if not self.get(fieldname):
				frappe.throw(_("Please set {0}").format(self.meta.get_label(fieldname)))

	def create_salary_slips(self):
		"""
			Creates salary slip for selected employees if already not created
		"""
		self.check_permission('write')
		self.created = 1
		emp_list = [d.employee for d in self.get_emp_list()]
		if emp_list:
			args = frappe._dict({
				"salary_slip_based_on_timesheet": self.salary_slip_based_on_timesheet,
				"payroll_frequency": self.payroll_frequency,
				"start_date": self.start_date,
				"end_date": self.end_date,
				"company": self.company,
				"posting_date": self.posting_date,
				"deduct_tax_for_unclaimed_employee_benefits": self.deduct_tax_for_unclaimed_employee_benefits,
				"deduct_tax_for_unsubmitted_tax_exemption_proof": self.deduct_tax_for_unsubmitted_tax_exemption_proof,
				"payroll_entry": self.name
			})
			if len(emp_list) > 30:
				frappe.enqueue(create_salary_slips_for_employees, timeout=600, employees=emp_list, args=args)
			else:
				create_salary_slips_for_employees(emp_list, args, publish_progress=False)
				# since this method is called via frm.call this doc needs to be updated manually
				self.reload()

	def get_sal_slip_list(self, ss_status, as_dict=False):
		"""
			Returns list of salary slips based on selected criteria
		"""
		cond = self.get_filter_condition()

		ss_list = frappe.db.sql("""
			select t1.name, t1.salary_structure from `tabSalary Slip` t1
			where t1.docstatus = %s and t1.start_date >= %s and t1.end_date <= %s
			and (t1.journal_entry is null or t1.journal_entry = "") and ifnull(salary_slip_based_on_timesheet,0) = %s %s
		""" % ('%s', '%s', '%s','%s', cond), (ss_status, self.start_date, self.end_date, self.salary_slip_based_on_timesheet), as_dict=as_dict)
		return ss_list

	def submit_salary_slips(self):
		self.check_permission('write')
		ss_list = self.get_sal_slip_list(ss_status=0)
		if len(ss_list) > 30:
			frappe.enqueue(submit_salary_slips_for_employees, timeout=600, payroll_entry=self, salary_slips=ss_list)
		else:
			submit_salary_slips_for_employees(self, ss_list, publish_progress=False)

	def email_salary_slip(self, submitted_ss):
		if frappe.db.get_single_value("HR Settings", "email_salary_slip_to_employee"):
			for ss in submitted_ss:
				ss.email_salary_slip()

	def get_loan_details(self):
		"""
			Get loan details from submitted salary slip based on selected criteria
		"""
		cond = self.get_filter_condition()
		return frappe.db.sql(""" select eld.loan_account, eld.loan,
				eld.interest_income_account, eld.principal_amount, eld.interest_amount, eld.total_payment,t1.employee
			from
				`tabSalary Slip` t1, `tabSalary Slip Loan` eld
			where
				t1.docstatus = 1 and t1.name = eld.parent and start_date >= %s and end_date <= %s %s
			""" % ('%s', '%s', cond), (self.start_date, self.end_date), as_dict=True) or []

	def get_salary_component_account(self, salary_component):
		account = frappe.db.get_value("Salary Component Account",
			{"parent": salary_component, "company": self.company}, "default_account")

		if not account:
			frappe.throw(_("Please set default account in Salary Component {0}")
				.format(salary_component))

		return account

	def get_salary_components(self, component_type):
		salary_slips = self.get_sal_slip_list(ss_status = 1, as_dict = True)
		if salary_slips:
			salary_components = frappe.db.sql("""select salary_component, amount, parentfield
				from `tabSalary Detail` where parentfield = '%s' and parent in (%s)""" %
				(component_type, ', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=True)
			return salary_components

	def get_salary_component_total(self, component_type = None):
		salary_components = self.get_salary_components(component_type)
		if salary_components:
			component_dict = {}
			for item in salary_components:
				add_component_to_accrual_jv_entry = True
				if component_type == "earnings":
					is_flexible_benefit, only_tax_impact = frappe.db.get_value("Salary Component", item['salary_component'], ['is_flexible_benefit', 'only_tax_impact'])
					if is_flexible_benefit == 1 and only_tax_impact ==1:
						add_component_to_accrual_jv_entry = False
				if add_component_to_accrual_jv_entry:
					component_dict[item['salary_component']] = component_dict.get(item['salary_component'], 0) + item['amount']
			account_details = self.get_account(component_dict = component_dict)
			return account_details

	def get_account(self, component_dict = None):
		account_dict = {}
		for s, a in component_dict.items():
			account = self.get_salary_component_account(s)
			account_dict[account] = account_dict.get(account, 0) + a
		return account_dict

	def get_default_payroll_payable_account(self):
		payroll_payable_account = frappe.get_cached_value('Company',
			{"company_name": self.company},  "default_payroll_payable_account")

		if not payroll_payable_account:
			frappe.throw(_("Please set Default Payroll Payable Account in Company {0}")
				.format(self.company))

		return payroll_payable_account

	def make_accrual_jv_entry(self):
		self.check_permission('write')
		earnings = self.get_salary_component_total(component_type = "earnings") or {}
		deductions = self.get_salary_component_total(component_type = "deductions") or {}
		default_payroll_payable_account = self.get_default_payroll_payable_account()
		loan_details = self.get_loan_details()
		jv_name = ""
		precision = frappe.get_precision("Journal Entry Account", "debit_in_account_currency")

		if earnings or deductions:
			journal_entry = frappe.new_doc('Journal Entry')
			journal_entry.voucher_type = 'Journal Entry'
			journal_entry.user_remark = _('Accrual Journal Entry for salaries from {0} to {1}')\
				.format(self.start_date, self.end_date)
			journal_entry.company = self.company
			journal_entry.posting_date = self.posting_date

			accounts = []
			payable_amount = 0

			# Earnings
			for acc, amount in earnings.items():
				payable_amount += flt(amount, precision)
				accounts.append({
						"account": acc,
						"debit_in_account_currency": flt(amount, precision),
						"party_type": '',
						"cost_center": self.cost_center,
						"project": self.project
					})

			# Deductions
			for acc, amount in deductions.items():
				payable_amount -= flt(amount, precision)
				accounts.append({
						"account": acc,
						"credit_in_account_currency": flt(amount, precision),
						"cost_center": self.cost_center,
						"party_type": '',
						"project": self.project
					})

			# Loan
			for data in loan_details:
				accounts.append({
						"account": data.loan_account,
						"credit_in_account_currency": data.principal_amount,
						"party_type": "Employee",
						"party": data.employee
					})

				if data.interest_amount and not data.interest_income_account:
					frappe.throw(_("Select interest income account in loan {0}").format(data.loan))

				if data.interest_income_account and data.interest_amount:
					accounts.append({
						"account": data.interest_income_account,
						"credit_in_account_currency": data.interest_amount,
						"cost_center": self.cost_center,
						"project": self.project,
						"party_type": "Employee",
						"party": data.employee
					})
				payable_amount -= flt(data.total_payment, precision)

			# Payable amount
			accounts.append({
				"account": default_payroll_payable_account,
				"credit_in_account_currency": flt(payable_amount, precision),
				"party_type": '',
				"cost_center": self.cost_center
			})

			journal_entry.set("accounts", accounts)
			journal_entry.title = default_payroll_payable_account
			journal_entry.save()

			try:
				journal_entry.submit()
				jv_name = journal_entry.name
				self.update_salary_slip_status(jv_name = jv_name)
			except Exception as e:
				frappe.msgprint(e)

		return jv_name

	def make_payment_entry(self):
		self.check_permission('write')

		cond = self.get_filter_condition()
		salary_slip_name_list = frappe.db.sql(""" select t1.name from `tabSalary Slip` t1
			where t1.docstatus = 1 and start_date >= %s and end_date <= %s %s
			""" % ('%s', '%s', cond), (self.start_date, self.end_date), as_list = True)

		if salary_slip_name_list and len(salary_slip_name_list) > 0:
			salary_slip_total = 0
			for salary_slip_name in salary_slip_name_list:
				salary_slip = frappe.get_doc("Salary Slip", salary_slip_name[0])
				for sal_detail in salary_slip.earnings:
					is_flexible_benefit, only_tax_impact, creat_separate_je, statistical_component = frappe.db.get_value("Salary Component", sal_detail.salary_component,
						['is_flexible_benefit', 'only_tax_impact', 'create_separate_payment_entry_against_benefit_claim', 'statistical_component'])
					if only_tax_impact != 1 and statistical_component != 1:
						if is_flexible_benefit == 1 and creat_separate_je == 1:
							self.create_journal_entry(sal_detail.amount, sal_detail.salary_component)
						else:
							salary_slip_total += sal_detail.amount
				for sal_detail in salary_slip.deductions:
					statistical_component = frappe.db.get_value("Salary Component", sal_detail.salary_component, 'statistical_component')
					if statistical_component != 1:
						salary_slip_total -= sal_detail.amount

				#loan deduction from bank entry during payroll
				salary_slip_total -= salary_slip.total_loan_repayment

			if salary_slip_total > 0:
				self.create_journal_entry(salary_slip_total, "salary")

	def create_journal_entry(self, je_payment_amount, user_remark):
		default_payroll_payable_account = self.get_default_payroll_payable_account()
		precision = frappe.get_precision("Journal Entry Account", "debit_in_account_currency")

		journal_entry = frappe.new_doc('Journal Entry')
		journal_entry.voucher_type = 'Bank Entry'
		journal_entry.user_remark = _('Payment of {0} from {1} to {2}')\
			.format(user_remark, self.start_date, self.end_date)
		journal_entry.company = self.company
		journal_entry.posting_date = self.posting_date

		payment_amount = flt(je_payment_amount, precision)

		journal_entry.set("accounts", [
			{
				"account": self.payment_account,
				"bank_account": self.bank_account,
				"credit_in_account_currency": payment_amount
			},
			{
				"account": default_payroll_payable_account,
				"debit_in_account_currency": payment_amount,
				"reference_type": self.doctype,
				"reference_name": self.name
			}
		])
		journal_entry.save(ignore_permissions = True)

	def update_salary_slip_status(self, jv_name = None):
		ss_list = self.get_sal_slip_list(ss_status=1)
		for ss in ss_list:
			ss_obj = frappe.get_doc("Salary Slip",ss[0])
			frappe.db.set_value("Salary Slip", ss_obj.name, "journal_entry", jv_name)

	def set_start_end_dates(self):
		self.update(get_start_end_dates(self.payroll_frequency,
			self.start_date or self.posting_date, self.company))

	def validate_employee_attendance(self):
		employees_to_mark_attendance = []
		days_in_payroll, days_holiday, days_attendance_marked = 0, 0, 0
		for employee_detail in self.employee_details:
			days_holiday = self.get_count_holidays_of_employee(employee_detail.employee)
			days_attendance_marked = self.get_count_employee_attendance(employee_detail.employee)
			days_in_payroll = date_diff(self.end_date, self.start_date) + 1
			if days_in_payroll > days_holiday + days_attendance_marked:
				employees_to_mark_attendance.append({
					"employee": employee_detail.employee,
					"employee_name": employee_detail.employee_name
					})
		return employees_to_mark_attendance

	def get_count_holidays_of_employee(self, employee):
		holiday_list = get_holiday_list_for_employee(employee)
		holidays = 0
		if holiday_list:
			days = frappe.db.sql("""select count(*) from tabHoliday where
				parent=%s and holiday_date between %s and %s""", (holiday_list,
				self.start_date, self.end_date))
			if days and days[0][0]:
				holidays = days[0][0]
		return holidays

	def get_count_employee_attendance(self, employee):
		marked_days = 0
		attendances = frappe.db.sql("""select count(*) from tabAttendance where
			employee=%s and docstatus=1 and attendance_date between %s and %s""",
			(employee, self.start_date, self.end_date))
		if attendances and attendances[0][0]:
			marked_days = attendances[0][0]
		return marked_days
