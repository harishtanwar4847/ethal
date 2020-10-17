# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "tg_steel"
app_title = "Tg Steel"
app_publisher = "Atrina Technologies Pvt. Ltd."
app_description = "Tg Steel"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "developers@atritechnocrat.in"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/tg_steel/css/tg_steel.css"
# app_include_js = "/assets/tg_steel/js/tg_steel.js"

# include js, css files in header of web template
# web_include_css = "/assets/tg_steel/css/tg_steel.css"
# web_include_js = "/assets/tg_steel/js/tg_steel.js"

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
# get_website_user_home_page = "tg_steel.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "tg_steel.install.before_install"
# after_install = "tg_steel.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "tg_steel.notifications.get_notification_config"

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
		"after_insert": "ethal.utils.before_save_asset_maintenance_log",
		"on_submit": "ethal.utils.create_stock_entry"
	},
	"Asset Repair": {
		"on_submit": "ethal.utils.create_stock_entry_from_asset_repair"
	},
	"Leave Allocation": {
		"on_submit": "ethal.utils.before_submit_leave_allocation"
	}
}


# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"tg_steel.tasks.all"
# 	],
# 	"daily": [
# 		"tg_steel.tasks.daily"
# 	],
# 	"hourly": [
# 		"tg_steel.tasks.hourly"
# 	],
# 	"weekly": [
# 		"tg_steel.tasks.weekly"
# 	]
# 	"monthly": [
# 		"tg_steel.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "tg_steel.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "tg_steel.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "tg_steel.task.get_dashboard_data"
# }

fixtures = [
	{
		"dt": "Custom Field",
		"filters": [
			[
				"dt",
				"in",
				["Supplier", "Customer", "Item", "Employee Tax Exemption Proof Submission", "Payment Entry", "Delivery Note", "Sales Invoice", "Sales Order", "Purchase Invoice", "Purchase Order", "Purchase Receipt", "Asset Repair", "Payment Entry", "Material Request", "Quotation Item", "Tax Category", "Address", "Print Settings", "Project", "Deleted Document", "Task", "Asset Maintenance Log", "Asset Maintenance Task"]
			]
		]
	},
	{
		"dt": "Print Format",
		"filters": [
			[
				"doc_type",
				"in",
				["Purchase Receipt"]
			]
		]
	},
	{
		"dt": "DocType",
		"filters": [
			[
				"name",
				"in",
				["Parts Used Item Table"]
			]
		]
	},
	{
		"dt": "Report",
		"filters": [
			[
				"name",
				"in",
				['Cash & Bank Balance']
			]
		]
	},
	"Translation",
	"Custom Script"
]
