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
