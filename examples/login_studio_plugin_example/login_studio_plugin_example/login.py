import frappe

from login_studio.api import Markup, escape

SUPPORT_EMAIL = "support@example.com"


def add_context(ls):
	# Values you put in ls are printed as-is by templates: escape anything that isn't trusted HTML
	ls["extra"]["support_email"] = escape(SUPPORT_EMAIL)


def help_notice(ls):
	email = ls["extra"].get("support_email")
	if not email:
		return ""
	link = Markup('<a href="mailto:{0}">{0}</a>').format(email)
	return Markup('<p class="lspe-help">{} {}</p>').format(frappe._("Need help signing in?"), link)
