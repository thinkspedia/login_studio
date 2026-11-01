import frappe
from frappe import _
from frappe.core.doctype.navbar_settings.navbar_settings import get_app_logo

from login_studio.render import build_page

no_cache = True
sitemap = 0


def get_context(context):
	# /login redirects signed-in users away, so layouts are previewed here with a sample form.
	# Not frappe.only_for: on v15 it lets everyone through while tests run.
	if "System Manager" not in frappe.get_roles():
		raise frappe.PermissionError

	settings = frappe.get_single("Login Studio Settings")
	name = frappe.form_dict.get("layout") or settings.active_layout
	if not name or not frappe.db.exists("Login Layout", name):
		raise frappe.DoesNotExistError(_("Login Layout {0} not found").format(name))

	layout = frappe.get_doc("Login Layout", name)
	context.title = _("Preview: {0}").format(layout.title)
	context.no_header = True
	context.full_width = True
	context.preview_layout = layout.name
	try:
		context.ls = build_page(settings, layout, stock_logo=get_app_logo())
	except Exception as e:
		# Only System Managers reach this page, so the reason is shown instead of logged
		context.ls = None
		context.preview_error = str(e)
	return context
