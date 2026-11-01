"""Branding values for the login page: colors, versions and fallbacks."""

import re

import frappe

HEX_COLOR_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")

DEFAULT_COLORS = {
	"primary": "#4338CA",
	"secondary": "#7C3AED",
	"accent": "#0EA5E9",
}

RADIUS = {"None": "0px", "Small": "6px", "Medium": "12px", "Large": "20px"}

# Shown when the Version Apps table is empty and the app is installed
DEFAULT_VERSION_APPS = {"frappe": "Frappe", "erpnext": "ERPNext", "hrms": "Frappe HR"}

DARK_TEXT = "#111827"
LIGHT_TEXT = "#FFFFFF"

RTL_LANGUAGES = {"ar", "fa", "he", "ps", "ur", "yi"}


def is_hex_color(value: str | None) -> bool:
	return bool(value and HEX_COLOR_RE.match(value))


def normalize_hex(value: str | None, default: str) -> str:
	if not is_hex_color(value):
		return default
	value = value.upper()
	if len(value) == 4:
		value = "#" + "".join(ch * 2 for ch in value[1:])
	return value


def relative_luminance(hex_color: str) -> float:
	"""WCAG 2.x relative luminance of a #RRGGBB color."""
	channels = [int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
	linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
	return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(a: str, b: str) -> float:
	la, lb = sorted((relative_luminance(a), relative_luminance(b)), reverse=True)
	return (la + 0.05) / (lb + 0.05)


def readable_text_on(background: str) -> str:
	"""Pick white or near-black text, whichever contrasts more with the background."""
	if contrast_ratio(background, LIGHT_TEXT) >= contrast_ratio(background, DARK_TEXT):
		return LIGHT_TEXT
	return DARK_TEXT


def is_http_url(value: str | None) -> bool:
	return bool(value) and value.lower().startswith(("https://", "http://"))


def text_direction(lang: str | None) -> str:
	return "rtl" if (lang or "").split("-")[0].lower() in RTL_LANGUAGES else "ltr"


def get_app_versions(rows) -> list[dict]:
	"""Versions of the configured apps that are installed on this site.

	``rows`` are Login Studio Version App rows; when empty, DEFAULT_VERSION_APPS is used.
	Apps that are not installed are skipped rather than shown as unknown.
	"""
	installed = set(frappe.get_installed_apps())
	wanted = [(row.app.strip(), row.label) for row in rows if row.app] or list(DEFAULT_VERSION_APPS.items())

	versions = []
	for app, label in wanted:
		if app not in installed:
			continue
		version = getattr(frappe.get_module(app), "__version__", None)
		if not version:
			continue
		title = label or DEFAULT_VERSION_APPS.get(app) or frappe.get_hooks("app_title", app_name=app)[0]
		versions.append({"app": app, "label": title, "version": version})
	return versions


def get_brand_name(settings) -> str:
	return (
		settings.brand_name
		or frappe.db.get_single_value("Website Settings", "app_name")
		or frappe.defaults.get_global_default("company")
		or frappe.local.site
	)


def get_logo(settings) -> str | None:
	return settings.logo or frappe.db.get_single_value("Website Settings", "app_logo")
