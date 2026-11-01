from frappe.www.login import get_context as get_stock_context

from login_studio.render import get_page_context

no_cache = True


def get_context(context):
	# Stock context first: providers, OTP, LDAP, signup and the logged-in redirect all stay upstream's
	get_stock_context(context)

	ls = get_page_context(context)
	context.ls = ls
	if ls:
		context.full_width = True
		if ls["logo"]:
			context.logo = ls["logo"]
	return context
