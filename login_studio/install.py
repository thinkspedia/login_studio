import frappe

from login_studio.layouts import remove_app_layouts, sync_layouts

DEFAULT_LAYOUT = "split_hero"


def after_install():
	sync_layouts()
	set_default_layout()


def after_migrate():
	sync_layouts()


def after_app_install(app_name):
	"""Pick up a plugin app's layouts as soon as it is installed, not only on the next migrate."""
	if app_name != "login_studio":
		sync_layouts(app_name)


def before_app_uninstall(app_name):
	if app_name != "login_studio":
		remove_app_layouts(app_name)


def set_default_layout():
	"""Frappe saves Singles with their field defaults before after_install runs, when no
	Login Layout exists yet, so the Link default is set here, after the layouts are synced."""
	if not frappe.db.get_single_value("Login Studio Settings", "active_layout"):
		frappe.db.set_single_value("Login Studio Settings", "active_layout", DEFAULT_LAYOUT)
