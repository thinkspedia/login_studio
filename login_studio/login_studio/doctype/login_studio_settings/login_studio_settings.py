# Copyright (c) 2026, Thinkspedia and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from login_studio import branding


class LoginStudioSettings(Document):
	def validate(self):
		for fieldname in ("primary_color", "secondary_color", "accent_color"):
			value = self.get(fieldname)
			if value and not branding.is_hex_color(value):
				frappe.throw(
					_("{0} must be a hex color like #4338CA.").format(_(self.meta.get_label(fieldname)))
				)

		if self.powered_by_url and not branding.is_http_url(self.powered_by_url):
			frappe.throw(_("Powered By URL must start with https:// or http://"))

		if self.enabled and self.active_layout:
			if not frappe.db.get_value("Login Layout", self.active_layout, "enabled"):
				frappe.throw(_("Layout {0} is disabled.").format(frappe.bold(self.active_layout)))
