"""Differences between supported Frappe major versions live here, nowhere else.

Login Studio supports Frappe v15 and v16 from one codebase. Code that must
behave differently per version imports a flag or helper from this module
instead of checking ``frappe.__version__`` itself.
"""

import frappe

SUPPORTED_MAJORS = (15, 16)

FRAPPE_MAJOR = int(frappe.__version__.split(".")[0])


def is_supported() -> bool:
	return FRAPPE_MAJOR in SUPPORTED_MAJORS


#: Path the desk lives under: v16 moved it from /app to /desk (and redirects /app/* there)
DESK_PATH = "/desk" if FRAPPE_MAJOR >= 16 else "/app"


def seed_desktop_icons():
	"""Create the missing Desktop Icons on v16, where the desk draws its app grid from them.

	Frappe seeds them only when an app is installed, so a site that installed Login Studio
	before it declared ``add_to_apps_screen`` never gets its icon. Frappe's own seeding is
	idempotent and does nothing unless the site's Desktop Page is the icon grid. v15 builds
	its apps screen from the hook on every request and needs nothing.
	"""
	if FRAPPE_MAJOR < 16:
		return

	from frappe.desk.doctype.desktop_icon.desktop_icon import create_desktop_icons

	create_desktop_icons()
