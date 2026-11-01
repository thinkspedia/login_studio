"""Public API for apps that extend Login Studio.

Everything importable from this module is stable: it only changes in a
backwards-incompatible way in a new major version of Login Studio. Anything
else in the package is internal and may change in any release.

See docs/plugins.md for the hooks (login_studio_layouts, login_studio_context,
login_studio_slots, login_studio_assets).
"""

import frappe
from markupsafe import Markup, escape

from login_studio import render

API_VERSION = 1

#: Slot names layouts offer to ``login_studio_slots`` hooks
SLOT_NAMES = render.SLOT_NAMES

__all__ = ["API_VERSION", "SLOT_NAMES", "Markup", "escape", "get_layout_context", "render_layout"]


def get_layout_context() -> dict:
	"""The ``ls`` object templates receive, built from the saved Login Studio Settings.

	Plugin context and slot hooks have already run on the returned value.
	"""
	return render.build_layout_context(frappe.get_cached_doc("Login Studio Settings"))


def render_layout(layout_name: str) -> dict:
	"""Render a layout with the saved settings, enabled or not.

	Returns ``{"before", "after", "css", "assets"}``: the page is ``before`` +
	the sign-in form + ``after``. Raises if the layout does not exist or fails
	to render.
	"""
	settings = frappe.get_cached_doc("Login Studio Settings")
	page = render.build_page(settings, frappe.get_doc("Login Layout", layout_name))
	return {key: page[key] for key in ("before", "after", "css", "assets")}
