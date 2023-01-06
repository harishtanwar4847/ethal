frappe.query_reports["Monthly Report of Raw material, packaging & components"] = {
    "filters": [
        {
            "fieldname":"month",
            "label":("Month"),
            "fieldtype":"Select",
            "options":[1,2,3,4,5,6,7,8,9,10,11,12],
            "default":1
        },
        {
			"fieldname":"year",
			"label": __("Year"),
			"fieldtype": "Link",
			"options":'Fiscal Year',
			"default": frappe.sys_defaults.fiscal_year
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
]
}