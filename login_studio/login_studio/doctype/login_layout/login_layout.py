# Copyright (c) 2026, Thinkspedia and contributors
# For license information, please see license.txt

import re

import frappe
from frappe import _
from frappe.model.document import Document

from login_studio.render import validate_layout

LAYOUT_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_]*$")


class LoginLayout(Document):
	def before_insert(self):
		# Only the file sync creates Standard / Plugin layouts; anything made in Desk is Custom
		if not self.flags.from_file_sync:
			self.source = "Custom"
			self.source_app = None

	def validate(self):
		if not LAYOUT_NAME_RE.match(self.layout_name or ""):
			frappe.throw(_("Layout Name may only contain lowercase letters, numbers and underscores."))

		if self.source in ("Standard", "Plugin"):
			if not self.flags.from_file_sync and (
				self.has_value_changed("template") or self.has_value_changed("css")
			):
				frappe.throw(
					_(
						"{0} layouts are shipped by an app and cannot be edited. Duplicate it to customize."
					).format(_(self.source))
				)
			return

		validate_layout(self.template, self.css)

	def on_trash(self):
		if self.source in ("Standard", "Plugin") and not frappe.flags.in_uninstall:
			frappe.throw(_("{0} layouts are shipped by an app and cannot be deleted.").format(_(self.source)))
		if frappe.db.get_single_value("Login Studio Settings", "active_layout") == self.name:
			frappe.throw(
				_("Layout {0} is active. Choose another layout first.").format(frappe.bold(self.name))
			)


@frappe.whitelist()
def duplicate_layout(source: str, layout_name: str, title: str) -> str:
	"""Copy any layout (Standard, Plugin or Custom) into a new editable Custom layout."""
	original = frappe.get_doc("Login Layout", source)
	original.check_permission("read")
	copy = frappe.get_doc(
		{
			"doctype": "Login Layout",
			"layout_name": layout_name,
			"title": title,
			"based_on": original.name,
			"description": original.description,
			"template": original.template,
			"css": original.css,
			"enabled": 1,
		}
	).insert()
	return copy.name
