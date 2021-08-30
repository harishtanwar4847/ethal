from erpnext.assets.doctype.asset_maintenance.asset_maintenance import AssetMaintenance
import frappe

def sync_maintenance_tasks(self):
    print('in custom file')
    tasks_names = []
    for task in self.get('asset_maintenance_tasks'):
        tasks_names.append(task.name)
        update_maintenance_log(asset_maintenance = self.name, item_code = self.item_code, item_name = self.item_name, task = task)
    asset_maintenance_logs = frappe.get_all("Asset Maintenance Log", fields=["name"], filters = {"asset_maintenance": self.name,
        "task": ("not in", tasks_names)})
    if asset_maintenance_logs:
        for asset_maintenance_log in asset_maintenance_logs:
            maintenance_log = frappe.get_doc('Asset Maintenance Log', asset_maintenance_log.name)
            maintenance_log.db_set('maintenance_status', 'Cancelled')


def update_maintenance_log(asset_maintenance, item_code, item_name, task):
	asset_maintenance_log = frappe.get_value("Asset Maintenance Log", {"asset_maintenance": asset_maintenance,
		"task": task.name, "maintenance_status": ('in',['Planned','Overdue'])})

	if not asset_maintenance_log:
		asset_maintenance_log = frappe.get_doc({
			"doctype": "Asset Maintenance Log",
			"asset_maintenance": asset_maintenance,
			"asset_name": asset_maintenance,
			"item_code": item_code,
			"item_name": item_name,
			"task": task.name,
			"has_certificate": task.certificate_required,
			"description_custom": task.description_custom,
			"assign_to_name": task.assign_to_name,
			"periodicity": str(task.periodicity),
			"maintenance_type": task.maintenance_type,
			"due_date": task.next_due_date
		})
		asset_maintenance_log.insert()
	else:
		maintenance_log = frappe.get_doc('Asset Maintenance Log', asset_maintenance_log)
		maintenance_log.assign_to_name = task.assign_to_name
		maintenance_log.has_certificate = task.certificate_required
		maintenance_log.description_custom = task.description_custom
		maintenance_log.periodicity = str(task.periodicity)
		maintenance_log.maintenance_type = task.maintenance_type
		maintenance_log.due_date = task.next_due_date
		maintenance_log.save()

AssetMaintenance.sync_maintenance_tasks = sync_maintenance_tasks
AssetMaintenance.update_maintenance_log = update_maintenance_log