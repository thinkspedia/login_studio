import frappe

from login_studio.layouts import sync_standard_layouts

DEFAULT_LAYOUT = "split_hero"


def after_install():
	sync_standard_layouts()
	set_default_layout()


def after_migrate():
	sync_standard_layouts()


def set_default_layout():
	"""Frappe saves Singles with their field defaults before after_install runs, when no
	Login Layout exists yet, so the Link default is set here, after the layouts are synced."""
	if not frappe.db.get_single_value("Login Studio Settings", "active_layout"):
		frappe.db.set_single_value("Login Studio Settings", "active_layout", DEFAULT_LAYOUT)
