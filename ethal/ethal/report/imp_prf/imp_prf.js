frappe.query_reports["Imp PRF"] = {
    "filters": [
        {
            "fieldname":"from_date",
            "label":("From Date"),
            "fieldtype":"Date",
            "default":frappe.datetime.month_start()
        },
        {
            "fieldname":"to_date",
            "label":("To Date"),
            "fieldtype":"Date",
            "default":frappe.datetime.get_today()
        },
        {
            "fieldname":"company",
            "label":("Company"),
            "fieldtype":"Link",
            "options":"Company",
            "default":"Ethal 2021"
        },
        {
            "fieldname":"purchase_from",
            "label":("Purchase From"),
            "fieldtype":"Select",
            "options":['ADDIS ABABA','DEBRE BIRHAN','IMPORT'],
            "default":"IMPORT"
        }
]
}