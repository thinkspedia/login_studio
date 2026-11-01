"""Layouts shipped as files, synced into the Login Layout DocType.

Each layout is a folder ``<name>/`` containing ``layout.json`` (title,
description), ``template.html`` (Jinja) and ``style.css``. Login Studio's own
folders are Standard layouts; folders registered by other apps through the
``login_studio_layouts`` hook are Plugin layouts.
"""

import json
import os

import frappe

STANDARD_LAYOUTS_PATH = os.path.dirname(__file__)


def read_layout_folder(path: str) -> dict:
	meta = json.loads(frappe.read_file(os.path.join(path, "layout.json"), raise_not_found=True))
	return {
		"title": meta["title"],
		"description": meta.get("description", ""),
		"template": frappe.read_file(os.path.join(path, "template.html"), raise_not_found=True),
		"css": frappe.read_file(os.path.join(path, "style.css")) or "",
	}


def get_layout_names(path: str) -> list[str]:
	return sorted(
		name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name, "layout.json"))
	)


def get_standard_layout_names() -> list[str]:
	return get_layout_names(STANDARD_LAYOUTS_PATH)


def get_layout_sources(app: str | None = None) -> list[tuple[str, str, str]]:
	"""(source, app, folder) for Login Studio's own layouts and every ``login_studio_layouts`` hook.

	Hook entries are paths relative to the app's Python package, e.g. ``"login_layouts"``.
	"""
	sources = []
	if app in (None, "login_studio"):
		sources.append(("Standard", "login_studio", STANDARD_LAYOUTS_PATH))

	for plugin_app in frappe.get_installed_apps():
		if plugin_app == "login_studio" or (app and plugin_app != app):
			continue
		app_path = os.path.realpath(frappe.get_app_path(plugin_app))
		for relative in frappe.get_hooks("login_studio_layouts", app_name=plugin_app) or []:
			folder = os.path.realpath(os.path.join(app_path, relative))
			if not folder.startswith(app_path + os.sep) or not os.path.isdir(folder):
				frappe.log_error(
					title="Login Studio: invalid login_studio_layouts entry",
					message=f"{plugin_app}: {relative!r} must be a folder inside the app package",
				)
				continue
			sources.append(("Plugin", plugin_app, folder))
	return sources


def sync_layouts(app: str | None = None) -> None:
	"""Create or update file-based layouts (all, or one app's). Keeps each layout's Enabled flag."""
	for source, source_app, folder in get_layout_sources(app):
		for name in get_layout_names(folder):
			owner = frappe.db.get_value("Login Layout", name, "source_app")
			if owner and owner != source_app:
				# Never let one app overwrite another app's (or a user's custom) layout
				frappe.log_error(
					title="Login Studio: layout name already taken",
					message=f"{source_app} ships layout {name!r}, but it already belongs to {owner}",
				)
				continue
			if owner is None and frappe.db.exists("Login Layout", name):
				# Existing Custom layout (source_app is empty) with the same name
				frappe.log_error(
					title="Login Studio: layout name already taken",
					message=f"{source_app} ships layout {name!r}, but a custom layout has that name",
				)
				continue

			data = read_layout_folder(os.path.join(folder, name))
			if owner:
				doc = frappe.get_doc("Login Layout", name)
			else:
				doc = frappe.new_doc("Login Layout")
				doc.layout_name = name
				doc.enabled = 1
			doc.update({**data, "source": source, "source_app": source_app})
			doc.flags.from_file_sync = True
			doc.flags.ignore_permissions = True
			doc.save()


def sync_standard_layouts() -> None:
	sync_layouts("login_studio")


def remove_app_layouts(app: str) -> None:
	"""Delete the Plugin layouts an app shipped; fall back to the default layout if one was active."""
	from login_studio.install import DEFAULT_LAYOUT

	names = frappe.get_all("Login Layout", filters={"source": "Plugin", "source_app": app}, pluck="name")
	if frappe.db.get_single_value("Login Studio Settings", "active_layout") in names:
		frappe.db.set_single_value("Login Studio Settings", "active_layout", DEFAULT_LAYOUT)
	for name in names:
		doc = frappe.get_doc("Login Layout", name)
		doc.flags.from_file_sync = True
		doc.flags.ignore_permissions = True
		doc.delete()
