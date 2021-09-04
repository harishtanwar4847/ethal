
frappe.ui.form.on('Sales Invoice', {
    fs_number: function (frm) {
        var a = frm.doc.fs_number;
        var mystr = a.replace(/\D/g, '');
        frm.set_value('fs_number', mystr);
        frm.refresh_field('fs_number')
    },
    before_save: function (frm) {
        console.log('items')
        var total_sales = 0;
        $.each(frm.doc.items || [], function (i, d) {
            total_sales += flt(d.total_net_weight);
        });
        frm.set_value("total_net_weight_aluminium", total_sales);
    },
    refresh: function(frm) {
        console.log('refresh')
    }
});


frappe.ui.form.on('Sales Invoice Item', {
    refresh(frm) {
        // your code here
    }
})