__version__ = "0.0.1"
from frappe.email.receive import InboundMail
import frappe
from axessio_erpnext.overrides import custom_create_reference_document

InboundMail._create_reference_document = custom_create_reference_document


