import frappe

from login_studio.layouts import sync_standard_layouts

DEFAULT_LAYOUT = "split_hero"


def after_install():
	sync_standard_layouts()
	set_default_settings()


def after_migrate():
	sync_standard_layouts()


def set_default_settings():
	"""Singles don't apply field defaults until first saved, so save them once on install."""
	settings = frappe.get_single("Login Studio Settings")
	for df in settings.meta.fields:
		if df.default and settings.get(df.fieldname) in (None, ""):
			settings.set(df.fieldname, df.default)
	if not settings.active_layout:
		settings.active_layout = DEFAULT_LAYOUT
	settings.flags.ignore_permissions = True
	settings.save()
