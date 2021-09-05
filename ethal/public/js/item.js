frappe.ui.form.on('Item', {
    diameter: function (frm) {
        weight(frm)
    },
    thickness: function (frm) {
        console.log("============")
        console.log(doc.name)
        weight(frm)
        refresh_field("standard_weight");
    },
    standard_weight: function (frm) {
        updateUOM(frm);
        console.log(doc.name)
    }

});
function updateUOM(frm) {
    var itemDocument = frm.doc
    console.log("in function update")


    if (frm.doc.uoms.length < "2") {
        console.log("In If of update")

        let d = frm.add_child("uoms");
        d.uom = "Nos";
        d.conversion_factor = itemDocument.standard_weight;
        refresh_field("uoms");
        console.log("print value of d", d);

        console.log("Leaving If of update")

    }
    else {
        console.log("In Else of update")
        console.log(frm.doc.uoms[1])
        frm.doc.uoms[1].conversion_factor = itemDocument.standard_weight;

        refresh_field("uoms");


        console.log("LEaving Else of update")

    }
}

function weight(frm) {
    var a = frm.doc;
    if (a.diameter !== 0 && a.thickness !== 0) {
        var w = 3.14 * (a.diameter / 2) * (a.diameter / 2) * a.thickness * (2700 / 1000000000);
        frm.set_value('standard_weight', w);
    }
    if (a.diameter === 0 || a.thickness === 0) {
        frm.set_value('standard_weight', '0');

    }
}