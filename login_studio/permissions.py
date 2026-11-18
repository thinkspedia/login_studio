import frappe


def has_app_permission() -> bool:
	"""Show Login Studio on the apps screen only to those who can edit its settings."""
	return "System Manager" in frappe.get_roles()
