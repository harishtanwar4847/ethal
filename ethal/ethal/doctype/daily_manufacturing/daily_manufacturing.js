// Copyright (c) 2023, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Daily Manufacturing', {
	refresh: function(frm) {
		if (frm.doc.receipts_of_this_month == undefined) {
			frappe.call({
				'method': 'ethal.ethal.doctype.daily_manufacturing.daily_manufacturing.get_previous_record',
				'args': {
					doc: frm.doc
				}
			})
			.success(success => {
				console.log(success.message[0])
				var data = success.message
				for (var i = 0; i < data.length; i++) {
					var childTable = cur_frm.add_child("receipts_of_this_month");
					childTable.item = data[i].item
					childTable.opening = data[i].closing	
					// childTable.items = l[i]
				}
				cur_frm.refresh_fields("receipts_of_this_month");
			})
		}
		if (frm.doc.shifts == undefined) {
			frappe.call({
				'method': 'ethal.ethal.doctype.daily_manufacturing.daily_manufacturing.get_previous_record_shift',
				'args': {
					doc: frm.doc
				}
			})
			.success(success => {
				console.log(success.message[0])
				var data = success.message
				for (var i = 0; i < data.length; i++) {
					var childTable = cur_frm.add_child("shifts");
					childTable.shift = data[i].shift
					childTable.ingot = data[i].ingot	
					// childTable.items = l[i]
				}
				cur_frm.refresh_fields("shifts");
			})
		}
		if (frm.doc.attendance == undefined) {
			frappe.call({
				'method': 'ethal.ethal.doctype.daily_manufacturing.daily_manufacturing.get_previous_record_attendence',
				'args': {
					doc: frm.doc
				}
			})
			.success(success => {
				console.log(success.message[0])
				var data = success.message
				for (var i = 0; i < data.length; i++) {
					var childTable = cur_frm.add_child("attendance");
					childTable.section = data[i].section
					childTable.type = data[i].type	
					// childTable.items = l[i]
				}
				cur_frm.refresh_fields("attendance");
			})
		}
		if (frm.doc.stock == undefined) {
			console.log("aala")
			frappe.call({
				'method': 'ethal.ethal.doctype.daily_manufacturing.daily_manufacturing.get_previous_record_stock',
				'args': {
					doc: frm.doc
				}
			})
			.success(success => {
				console.log(success.message[0])
				var data = success.message
				for (var i = 0; i < data.length; i++) {
					var childTable = cur_frm.add_child("stock");
					childTable.item = data[i].item
					// childTable.items = l[i]
				}
				cur_frm.refresh_fields("stock");
			})
		}


	}
});
