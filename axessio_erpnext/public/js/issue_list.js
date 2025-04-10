
// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// render
frappe.listview_settings["Issue"] = {
	// add_fields: [
	// 	"customer",
	// 	"customer_name",
	// 	"base_grand_total",
	// 	"outstanding_amount",
	// 	"due_date",
	// 	"company",
	// 	"currency",
	// 	"is_return",
	// ],
	get_indicator: function (doc) {
		const status_colors = {
            beauftragt: "green",
            "nicht begonnen": "orange",
            "erledigt": "red",
           "angefangen": "blue",
            "wiederkehrend": "yellow",
			
		};
		return [__(doc.status), status_colors[doc.status], "status,=," + doc.status];
	},

	// onload: function (listview) {
	// 	listview.page.add_action_item(__("Delivery Note"), () => {
	// 		erpnext.bulk_transaction_processing.create(listview, "Sales Invoice", "Delivery Note");
	// 	});

	// 	listview.page.add_action_item(__("Payment"), () => {
	// 		erpnext.bulk_transaction_processing.create(listview, "Sales Invoice", "Payment Entry");
	// 	});
	// },
};
