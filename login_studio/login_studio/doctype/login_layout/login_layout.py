# Copyright (c) 2026, Thinkspedia and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class LoginLayout(Document):
	def validate(self):
		if self.source in ("Standard", "Plugin") and not self.flags.from_file_sync:
			if self.has_value_changed("template") or self.has_value_changed("css"):
				frappe.throw(
					_(
						"{0} layouts are shipped by an app and cannot be edited. Duplicate it to customize."
					).format(_(self.source))
				)

		if "login_form" not in (self.template or ""):
			frappe.throw(_("The template must output {0}.").format("<code>{{ login_form }}</code>"))

	def on_trash(self):
		if self.source in ("Standard", "Plugin") and not frappe.flags.in_uninstall:
			frappe.throw(_("{0} layouts are shipped by an app and cannot be deleted.").format(_(self.source)))
