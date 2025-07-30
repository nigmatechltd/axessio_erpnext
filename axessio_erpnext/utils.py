import frappe
import json
from frappe import _


@frappe.whitelist()
def create_issue(dialog_values,description,docname):
    
    if dialog_values and description:
        if isinstance(dialog_values,str):
            dialog_values = json.loads(dialog_values)
            
        issue = frappe.get_doc({
            "doctype" : "Issue",
            "subject" : dialog_values.get("subject"),
            "person_in_charge" : dialog_values.get("employee_in_charge"),
            "issue_type" : dialog_values.get("issue_type"),
            "description" : description,
            "priority" : dialog_values.get("priority"),
            "status" : dialog_values.get("status"),
            "property_name" : dialog_values.get("property_unit")
            
        })
    issue.insert()
    frappe.db.commit()
    frappe.db.set_value("Communication",docname,"reference_doctype","Issue")
    frappe.db.set_value("Communication",docname,"reference_name",issue.name)
    

@frappe.whitelist()
def create_po(dialog_values,doc):
    
    if isinstance(dialog_values,str):
        dialog_values = json.loads(dialog_values)
    
    if isinstance(doc,str):
        doc = json.loads(doc)
    
    purchase_items = []
   
    if dialog_values.get("purchase_order_item"):
        for item in dialog_values.get("purchase_order_item"):
            pot = frappe.get_doc({
                "doctype" : "Purchase Order Item",
                "item_code" : item.get("item"),
                "qty" : item.get("qty"),
                "rate" : item.get("rate"),
                "amount" : float(item.get("qty",0)) * float(item.get("rate",0)),
                "parentfield": "items",
                "item_name" : frappe.db.get_value("Item",item.get("item"),"item_name"),
                "uom" : frappe.db.get_value("Item",item.get("item"),"stock_uom"),
                "schedule_date" : dialog_values.get("required_by"),
                "parenttype": "Purchase Order",
            })
            pot.flags.ignore_mandatory = True
            purchase_items.append(pot)
    
    po = frappe.get_doc({
        "doctype" : "Purchase Order",
        "supplier" : dialog_values.get("supplier"),
        "custom_issue" : doc.get("name"),
        "custom_subject" : doc.get("subject"),
        "custom_priority" : doc.get("priority"),
        "custom_rental_unit" : doc.get("property_name"),
        "custom_resubmission_date": doc.get("opening_date"),
        "custom_ticket_customer" : doc.get("customer"),
        "custom_axessio_contact_person" : doc.get("person_in_charge"),
        "custom_description" : doc.get("description"),
        "custom_type_of_order" : "External", #dialog_values.get("type_of_order"),
        "schedule_date" : dialog_values.get("required_by"),
        "items":purchase_items
    })
    po.flags.ignore_validate=True
    po.flags.ignore_mandatory = True
    po.insert()
    
    app_url = frappe.utils.get_url_to_form("Purchase Order", po.name)
    hyperlink = '<a href="{url}" target="_blank">{name}</a>'.format(
        url=app_url, name=po.name
    )
    comment = "Bestellung erzeugt {hyperlink}".format(hyperlink=hyperlink)
    
    comment_doc = frappe.get_doc({
        "doctype" : "Comment",
        "reference_doctype" : "Issue",
        "reference_name" : doc.get("name"),
        "comment_by" : frappe.session.user_fullname,
        "content" : _(comment),
        "comment_email":frappe.session.user,
        "comment_type" : "Comment"
    })
    comment_doc.save()
    frappe.db.commit()
    return po.name
    

@frappe.whitelist()
def create_mv(dialog_values,doc):
    
    if isinstance(dialog_values,str):
        dialog_values = json.loads(dialog_values)
    
    if isinstance(doc,str):
        doc = json.loads(doc)
    
    mv_items = []
    if dialog_values.get("maintenance_visit_item"):
        
        for item in dialog_values.get("maintenance_visit_item"):
            
            mv_item = frappe.get_doc({
                "doctype" : "Maintenance Visit Purpose",
                "item_code" : item.get("item"),
                "item_name" : frappe.db.get_value("Item",item.get("item"),"item_name"),
                "description" : item.get("description"),
                "parentfield" : "purposes",
                "parenttype" : "Maintenance Visit"
                
            })
            mv_items.append(mv_item)
            
            
    m_visit = frappe.get_doc({
            "doctype" : "Maintenance Visit",
            "customer" : dialog_values.get("customer"),
            "company" : dialog_values.get("company"),
            "custom_type_of_work_order" : "Internal", #dialog_values.get("type_of_order"),
            "mntc_date" : dialog_values.get("date"),
            "custom_property_unit" : doc.get("property_name"),
            "custom_issue" : doc.get("name"),
            "custom_issue_description" : remove_html_tags(doc.get("description")),
            "custom_axessio_contact_person" : dialog_values.get("axessio_contact_person"),
            "custom_employee" : dialog_values.get("employee"),
            "purposes"  : mv_items,
            "custom_lease" : doc.get("custom_lease")
            
        })
    m_visit.flags.ignore_validate=True
    m_visit.flags.ignore_mandatory = True
    m_visit.insert()
    
    app_url = frappe.utils.get_url_to_form("Maintenance Visit", m_visit.name)
    hyperlink = '<a href="{url}" target="_blank">{name}</a>'.format(
        url=app_url, name=m_visit.name
    )
    comment = "Maintenance Visit created {hyperlink}".format(hyperlink=hyperlink)
    
    comment_doc = frappe.get_doc({
        "doctype" : "Comment",
        "reference_doctype" : "Issue",
        "reference_name" : doc.get("name"),
        "comment_by" : frappe.session.user_fullname,
        "content" : _(comment),
        "comment_email":frappe.session.user,
        "comment_type" : "Comment"
    })
    comment_doc.save()
    frappe.db.commit()
    return m_visit.name


def remove_html_tags(text):
	import re
	clean = re.compile('<.*?>')
	return re.sub(clean, '', text)  

@frappe.whitelist()
def get_company_default_billing_address(company):
    
    company = frappe.db.get_value("Dynamic Link",{"link_doctype":"Company","link_name":company},"parent")
    return company
