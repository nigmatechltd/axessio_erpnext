__version__ = "0.0.1"
from frappe.email.receive import InboundMail
import frappe
from axessio_erpnext.overrides import CustomInboundMail
InboundMail = CustomInboundMail


