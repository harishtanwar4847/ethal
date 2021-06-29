# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "ethal"
app_title = "Ethal"
app_publisher = "Atrina Technologies Pvt. Ltd."
app_description = "Ethal"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "developers@atritechnocrat.in"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/ethal/css/ethal.css"
# app_include_js = "/assets/ethal/js/ethal.js"

app_include_js = "/assets/ethal/js/transaction.js"

# include js, css files in header of web template
# web_include_css = "/assets/ethal/css/ethal.css"
# web_include_js = "/assets/ethal/js/ethal.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "ethal.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "ethal.install.before_install"
# after_install = "ethal.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "ethal.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }
doc_events = {
	"Asset Maintenance Log": {
		"after_insert": "ethal.assets.before_save_asset_maintenance_log",
		"on_submit": "ethal.assets.create_stock_entry"
	},
	"Asset Repair": {
		"on_submit": "ethal.assets.create_stock_entry_from_asset_repair"
	},
	"Leave Allocation": {
		"on_submit": "ethal.hr.before_submit_leave_allocation"
	},
	"*": {
		"before_submit": "ethal.accounts.before_submit_all_doctypes"
	},
	"Payroll Entry": {
		"before_submit": "ethal.hr.update_salary_structure_assignment_rate"
	},
	"Salary Slip": {
		"before_insert": "ethal.hr.before_insert_salary_slip",
		"get_emp_and_leave_details": "ethal.hr.before_save_salary_slip",
		"before_save": "ethal.hr.before_save"
	},
	"Employee": {
		"after_insert": "ethal.hr.set_payeename"
	},
	"Employee Promotion": {
		"on_submit": "ethal.hr.on_update_employee_promotion"
	},
	"Interview Configuration": {
        "before_save": "ethal.ethal.doctype.interview_configuration.interview_configuration.generate_round_numbers"
    },
	"Payment Entry": {
		"validate": "ethal.accounts.before_insert_payment_entry",
		"before_submit": "ethal.accounts.set_approver_name"
	},
	# "Stock Entry": {
	# 	"before_submit": "ethal.accounts.before_submit_stock_entry"
	# },
	"Sales Invoice": {
		"validate": "ethal.accounts.before_insert_sales_invoice",
		"before_submit": "ethal.accounts.set_approver_name"
	},
	"Sales Order": {
		"before_submit": "ethal.accounts.set_approver_name"
	},
	"Purchase Order": {
		"before_submit": "ethal.accounts.set_approver_name",
	},	
	"Purchase Invoice": {
		"before_submit": "ethal.accounts.set_approver_name"
	},
	"Material Request": {
		"before_submit": "ethal.accounts.set_approver_name"
	},
	"Journal Entry": {
		"before_submit": "ethal.accounts.set_approver_name"
	},
	"Payment Request and Authorization": {
		"before_submit": "ethal.utils.set_approver_name"
	},
	"Attendance": {
		"before_submit": "ethal.hr.trigger_mail_if_absent_consecutive_5_days"
	},
	"Salary Structure Assignment": {
		"on_submit": "ethal.hr.before_insert_salary_structure_assignment"
	},
	"Vehicle Log": {
		"on_update": "ethal.hr.before_update_vehicle_log"
	},
	"Customer": {
		"after_insert": "ethal.utils.set_payeename"
	},
	"Supplier": {
		"after_insert": "ethal.utils.supplier_set_payeename"
	},
	"Shareholder": {
		"after_insert": "ethal.utils.shareholder_set_payeename"
	}
}

# on_login = 'ethal.hr.successful_login'

doctype_list_js = {
    "Salary Structure Assignment" : "public/js/salary_structure_assignment_list.js",
	"Employee" : "public/js/employee_list.js"
}

override_doctype_dashboards = {
	"Job Applicant": "ethal.hr.override_job_applicant_dashboard"
}

permission_query_conditions = {
    "Interview Round form": "ethal.ethal.doctype.interview_round.interview_round.interview_round_permissions_query_conditions"
}

scheduler_events = {
	"cron": {
		"59 11 * * 0": [
			"ethal.hr.shift_rotate"
		]
	},
	"hourly": [
        "ethal.ethal.employee_checkin.process_auto_attendance_for_holidays"
		# "ethal.hr.shift_rotate"
    ],
	"daily": [
		"ethal.ethal.doctype.contract_management.contract_management.send_reminder_mail_to_user"
	]
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"ethal.tasks.all"
# 	],
# 	"daily": [
# 		"ethal.tasks.daily"
# 	],
# 	"hourly": [
# 		"ethal.tasks.hourly"
# 	],
# 	"weekly": [
# 		"ethal.tasks.weekly"
# 	]
# 	"monthly": [
# 		"ethal.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "ethal.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "ethal.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "ethal.task.get_dashboard_data"
# }

fixtures = [
	{
		"dt": "Custom Field",
		"filters": [
			[
				"dt",
				"in",
				["Shareholder", "Landed Cost Voucher", "Vehicle Log", "Supplier", "Customer", "Payroll Entry", "Employee", "Job Opening", "Employee Grade", "Salary Structure Assignment", "Employee Tax Exemption Proof Submission", "Payment Entry", "Print Settings", "Purchase Order", "Sales Order", "Sales Invoice", "Sales Invoice Item", "Material Request", "Purchase Receipt", "Journal Entry"]
			]
		]
	},
	{
		"dt": "Print Format",
		"filters": [
			[
				"doc_type",
				"in",
				["Delivery Note", "Journal Entry", "Purchase Receipt", "Sales Order", "Sales Invoice", "Payment Entry", "Purchase Order", "Purchase Invoice", "Material Request", "Payment Request and Authorization", "Quotation"]
			]
		]
	},
	{
		"dt": "Workflow",
		"filters": [
			[
				"document_type",
				"in",
				["Delivery Note", "Journal Entry", "Sales Order", "Sales Invoice", "Payment Entry", "Purchase Order", "Purchase Invoice", "Material Request", "Payment Request and Authorization"]
			]
		]
	},
	{
		"dt": "Role",
		"filters": [
			[
				"name",
				"in",
				['Delivery Note Approver', 'EOS User', 'EOS Manager', 'Journal Entry Approver', 'Deputy PRA Approver', 'Accounts Viewer', 'Purchase Order Approver', 'PRA Approver', 'PRA Checker', 'CFO', 'Material Request Approver', 'Sales Invoice Approver', 'Sales Order Approver', 'Payment Entry Approver', 'Purchase Invoice Approver', 'CRV Approver', 'PCPV Approver', 'Chart of Accounts Manager', 'Document Deletor', 'Document canceller', 'Petty Cash Manager']
			]
		]
	},
	{
		"dt": "Custom Script",
		"filters": [
			[
			"dt",
			"in",
			['Payment Entry', 'Customer', 'Supplier', 'Shareholder', 'Landed Cost Voucher', 'Vehicle Log', 'Employee', 'Salary Structure', 'Salary Structure Assignment', 'Job Applicant', 'Job Opening', 'Salary Slip', 'Purchase Invoice', 'Sales Invoice', 'Asset Maintenance Log', 'Asset Repair', 'Quotation', 'Delivery Note', 'Item']
			]
		]
	},
	{
		"dt": "Employee Prerequisite Document",
		"filters": [
			[
				"name",
				"in",
				['TIN No', 'Pension No', 'Appointment Letter', 'Medical Certificate', 'Job Description']
			]
		]
	},
	"Translation",
	"Shift Type",
]