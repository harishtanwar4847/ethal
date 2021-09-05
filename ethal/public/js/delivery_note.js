frappe.ui.form.on('Delivery Note', {
	po_no:function(frm) {
		var a = frm.doc.po_no;
		
		console.log("type of a -->",typeof a);
		
		var mystr = a.replace(/\D/g,'');
		console.log("removed alphabets-->",mystr);
		frm.set_value('po_no',mystr);
		frm.refresh_field('po_no')
    }
})