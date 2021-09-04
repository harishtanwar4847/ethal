frappe.ui.form.on('Asset Maintenance Log', {
	refresh(frm) {
        console.log('refrsh')
	if (frm.doc.docstatus===0) {
			frm.add_custom_button(__('Stock Entry'), function() {
			   new frappe.ui.form.MultiSelectDialog({
                    doctype: "Stock Entry",
                    target: frm,
                    setters: {},
                    date_field: "posting_date",
                    get_query() {
                        return {
                            filters: { docstatus: ['!=', 2] }
                        }
                    },
                    action(selections) {
                        console.log(selections);
                       console.log(typeof(selections))
                       for (var i in selections){
                           console.log(selections[i])
                           frappe.call({
                               method: "ethal.assets.set_items_from_stock_entry",
                               args: {
                                   name: selections[i]
                               },
                               callback: function(r){
                                   console.log(r.message)
                                  let op = r.message
                                //   me.frm.add_child("part_used").item = op['item_code'];
                                //   me.frm.refresh_field("part_used");
                                var childTable = cur_frm.add_child("part_used");
                                childTable.item=op['item_code']
                                childTable.item_name=op['item_name']
                                childTable.stock_entry = op['parent']
                                childTable.item_group=op['item_group']
                                childTable.dscription=op['description']
                                childTable.uom=op['uom']
                                childTable.quantity=op['qty']
                                cur_frm.refresh_fields("part_used");
                                $('.modal').hide();
                               }
                           })
                    }
                    }
                });
			}, __("Get items from"));
	}
    }
})