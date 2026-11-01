"""Layouts shipped as files, synced into the Login Layout DocType.

Each layout is a folder ``<name>/`` containing ``layout.json`` (title,
description), ``template.html`` (Jinja) and ``style.css``.
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


def get_standard_layout_names() -> list[str]:
	return sorted(
		name
		for name in os.listdir(STANDARD_LAYOUTS_PATH)
		if os.path.isfile(os.path.join(STANDARD_LAYOUTS_PATH, name, "layout.json"))
	)


def sync_standard_layouts() -> None:
	"""Create or update the Standard layouts from files. Keeps each layout's Enabled flag."""
	for name in get_standard_layout_names():
		data = read_layout_folder(os.path.join(STANDARD_LAYOUTS_PATH, name))
		if frappe.db.exists("Login Layout", name):
			doc = frappe.get_doc("Login Layout", name)
		else:
			doc = frappe.new_doc("Login Layout")
			doc.layout_name = name
			doc.enabled = 1
		doc.update({**data, "source": "Standard", "source_app": "login_studio"})
		doc.flags.from_file_sync = True
		doc.flags.ignore_permissions = True
		doc.save()
