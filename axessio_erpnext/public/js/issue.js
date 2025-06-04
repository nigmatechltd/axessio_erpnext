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
              options : "Item"
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
            // {
            //     fieldname: "total",
            //     fieldtype: "Currency",
            //     in_list_view: 1,
            //     label: __("Total"),

            // },
          ];
        this.data = [];
		var d = new frappe.ui.Dialog({
			title: __("Create Purchase Order"),
			fields: [
				{
					fieldtype: "Select",
					label: __("Type of Order"),
					fieldname: "type_of_order",
                    options : ["","Internal","External",]
					
				},
				{
					fieldtype: "Link",
					options: "Supplier",
					label: __("Supplier"),
					fieldname: "supplier",
                    default : frm.doc.sub_contractor_contact
				},
                {
					fieldtype: "Date",
					
					label: __("Required By"),
					fieldname: "required_by",
                    default : "Today"
				},
                {
					fieldtype: "Table",
					label: __("Purchase Order Item"),
					fieldname: "purchase_order_item",
                    in_place_edit : true,
                    cannot_add_rows : false,
                    fields : table_fields,
                    get_data: () => {
                        return this.data;
                    },
                    
				},
              
			],
		});
		d.set_primary_action(__("Create Purchase Order"), function () {
			var values = d.get_values();
			if (values) {
				frappe.confirm(
					__("Are you sure you want to create an purchase order from this issue?",),
					function () {
						d.hide();
						frappe.call({
							method: "axessio_erpnext.utils.create_po",
							args: {
								"doc": frm.doc,
								"dialog_values" : values
                                
							},
							callback: function () {
                                frappe.show_alert({
                                    message: __("Purchase Order Created"),
                                    indicator: "info",
                                });
                                cur_frm.reload_doc()
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
		d.show();
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
					label: __("Type of Order"),
					fieldname: "type_of_order",
                    options : ["","Internal","External",]
					
				},
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
					options: "Employee",
					label: __("Axessio Contact Person"),
					fieldname: "axessio_contact_person",
					default : frm.doc.person_in_charge

				},
                {
					fieldtype: "Link",
					options: "Employee",
					label: __("Employee"),
					fieldname: "employee",
				},
                {
					fieldtype: "Date",
					label: __("Maintenance Date"),
					fieldname: "maintenance_date",
                    default : "Today"
				},
                {
					fieldtype: "Table",
					label: __("Maintenance Visit Item"),
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
					__("Are you sure you want to create an maintenance visit from this issue?",),
					function () {
						d.hide();
						frappe.call({
							method: "axessio_erpnext.utils.create_mv",
							args: {
								"doc": frm.doc,
								"dialog_values" : values
                                
							},
                            freeze:true,
							callback: function () {
                                frappe.show_alert({
                                    message: __("Maintenance Visit Created"),
                                    indicator: "info",
                                });
                                cur_frm.reload_doc()
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
		d.show();
	},

})