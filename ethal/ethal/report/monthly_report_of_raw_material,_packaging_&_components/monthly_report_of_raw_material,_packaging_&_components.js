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
            "label":("Year"),
            "fieldtype":"Select",
            "options":[2020,2021,2022,2023],
            "default":2023
        },
]
}