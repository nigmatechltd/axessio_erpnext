frappe.ui.form.on("Issue",{

    refresh : function(frm){
        cur_frm.add_custom_button(__("Create Purchase Order"), function(){
            frm.trigger("create_purchase_order")
        },"Issue Actions")

        cur_frm.add_custom_button(__("Create Maintenance Visit"), function(){
            frm.trigger("create_maintenance_visit")
        },"Issue Actions")
    },

	create_purchase_order: function (frm) {
		const table_fields = [
			{
				fieldname: "item",
				fieldtype: "Link",
				in_list_view: 1,
				label: __("Item"),
				options: "Item"
			},
			{
				fieldname: "uom",
				fieldtype: "Link",
				in_list_view: 1,
				label: __("UOM"),
				options: "UOM"
			},
			{
				fieldname: "qty",
				fieldtype: "Float",
				in_list_view: 1,
				label: __("Quantity"),
			},
			{
				fieldname: "rate",
				fieldtype: "Currency",
				in_list_view: 1,
				label: __("Rate"),
			},
		];

		this.data = [];
		frappe.db.exists("Item", "auf Nachweis").then(exists => {
			if (exists) {
				frappe.db.get_doc("Item", "auf Nachweis").then(item => {
					this.data.push({
						item: item.name,
						uom: item.stock_uom,
						qty: 1,
						rate: item.valuation_rate,
					});
				});
			}
		});

		let d = new frappe.ui.Dialog({
			title: __("Create Purchase Order"),
			fields: [
				{
					fieldtype: "Link",
					options: "Supplier",
					label: __("Supplier"),
					fieldname: "supplier",
					default: frm.doc.sub_contractor_contact
				},
				{
					fieldtype: "Date",
					label: __("Required By"),
					fieldname: "required_by",
					default: "Today"
				},
				{
					fieldtype: "Table",
					label: __("Purchase Order Item"),
					fieldname: "purchase_order_item",
					in_place_edit: true,
					cannot_add_rows: false,
					fields: table_fields,
					get_data: () => this.data
				},
			],
			primary_action_label: __("Create Purchase Order"),
			primary_action(values) {
				if (values) {
					frappe.confirm(
						__("Wollen Sie wirklich eine Bestellung anlegen?"),
						function () {
							d.hide();
							frappe.call({
								method: "axessio_erpnext.utils.create_po",
								args: {
									"doc": frm.doc,
									"dialog_values": values
								},
								callback: function (r) {
									frappe.show_alert({
										message: __("Purchase Order Created"),
										indicator: "info",
									});
									if (r.message) {
										frappe.set_route('Form', 'Purchase Order', r.message);
									}
								}
							});
						},
						function () {
							frappe.show_alert({
								message: __("Purchase Order not Created"),
								indicator: "info",
							});
							d.hide();
						}
					);
				}
			}
		});

		d.show();
		d.refresh_field("purchase_order_item");
	},
	
    create_maintenance_visit: function (frm) {

        const table_fields = [
            {
              fieldname: "item",
              fieldtype: "Link",
              in_list_view: 1,
              label: __("Item"),
              options : "Item"
            },
            {
                fieldname: "description",
                fieldtype: "Data",
                in_list_view: 1,
                label: __("description"),
               
                
            },
            // {
            //     fieldname: "total",
            //     fieldtype: "Currency",
            //     in_list_view: 1,
            //     label: __("Total"),

            // },
          ];
        this.data = [];
		var d = new frappe.ui.Dialog({
			title: __("Create Maintenance Visit"),
			fields: [
				
                {
					fieldtype: "Select",
					label: __("Maintenance Type"),
					fieldname: "maintenance_type",
                    options : ["","Scheduled","Unscheduled","Breakdown"]
					
				},
				{
					fieldtype: "Link",
					options: "Customer",
					label: __("Customer"),
					fieldname: "customer",
					default : frm.doc.customer
				},
				{
					fieldtype: "Link",
					options: "Company",
					label: __("Company"),
					fieldname: "company",
					default : frm.doc.custom_property_company
				},
                {
					fieldtype: "Link",
					options: "Employee",
					label: __("Contact Person"),
					fieldname: "contact_person",
					default : frm.doc.person_in_charge

				},
                {
					fieldtype: "Link",
					options: "User",
					label: __("Property Manager"),
					fieldname: "property_manager",
					default : frappe.session.user
				},
                {
					fieldtype: "Date",
					label: __("Maintenance Date"),
					fieldname: "maintenance_date",
                    default : "Today"
				},
                {
					fieldtype: "Table",
					label: __("Wartungsbesuch"),
					fieldname: "maintenance_visit_item",
                    in_place_edit : true,
                    cannot_add_rows : false,
                    fields : table_fields,
                    get_data: () => {
                        return this.data;
                    },
                    
				},
              
			],
		});
		d.set_primary_action(__("Create Maintenance Visit"), function () {
			var values = d.get_values();
			if (values) {
				frappe.confirm(
					__("Wollen Sie wirklich einen Wartungsbesuch für diesen Vorgang erstellen?",),
					function () {
						d.hide();
						frappe.call({
							method: "axessio_erpnext.utils.create_mv",
							args: {
								"doc": frm.doc,
								"dialog_values" : values
                                
							},
                            freeze:true,
							callback: function (r) {
                                frappe.show_alert({
                                    message: __("Wartungsbesuch angelegt"),
                                    indicator: "info",
                                });
								if (r.message) {
									frappe.set_route('Form', 'Maintenance Visit', r.message);
								}
								// cur_frm.refresh();
                                // cur_frm.refresh_fields()

							},
						});
					},
					function () {
						frappe.show_alert({
							message: __("Purchase Order not Created"),
							indicator: "info",
						});
                        d.hide()
					}
				);
			}
		});

		// if (frm.doc.property_name) {
		// 		frappe.db.get_doc("Property", frm.doc.property_name).then(property => {
		// 			if (property.company) {
		// 				d.set_value("company", property.company);
		// 			}
		// 		});
		// 	}

		d.show();
	},

})