"""Builds the Login Studio part of the /login page.

The layout is rendered here, in Python, with a placeholder where the stock
Frappe login form goes. The HTML is split at the placeholder and
``www/login.html`` outputs ``before``, the upstream form (``super()``) and
``after``, so the form itself is never copied.

Any failure returns ``None`` and the page falls back to the stock login.
"""

import os

import frappe
from frappe import _
from frappe.utils.jinja import get_jenv, safe_render_flags
from jinja2 import TemplateSyntaxError
from markupsafe import Markup, escape

from login_studio import branding
from login_studio.layouts import STANDARD_LAYOUTS_PATH

FORM_TOKEN = "<!--login-studio:login-form-->"

MAX_TEMPLATE_SIZE = 100_000
MAX_CSS_SIZE = 200_000

ERROR_LOG_CACHE_KEY = "login_studio:last_render_error"
ERROR_LOG_INTERVAL = 300  # seconds; a broken layout must not flood Error Log on every visit


def get_page_context(context) -> dict | None:
	"""Login Studio context for the page, or None to render the stock login."""
	if frappe.conf.get("login_studio_disabled"):
		return None

	try:
		settings = frappe.get_cached_doc("Login Studio Settings")
		if not settings.enabled or not settings.active_layout:
			return None

		layout = frappe.get_cached_doc("Login Layout", settings.active_layout)
		if not layout.enabled:
			return None

		return build_page(settings, layout, stock_logo=context.get("logo"))
	except Exception:
		log_render_error()
		return None


def build_page(settings, layout, stock_logo: str | None = None) -> dict:
	"""Render ``layout`` with ``settings``. Raises on any error; callers decide how to fail."""
	ls = build_layout_context(settings, stock_logo=stock_logo)
	html = render_layout(layout.template, ls)
	if html.count(FORM_TOKEN) != 1:
		raise ValueError(_("The template must output {0} exactly once.").format("{{ login_form }}"))
	before, after = html.split(FORM_TOKEN)

	return {
		"before": Markup(before),
		"after": Markup(after),
		"css": Markup(build_css(settings, layout)),
		"logo": ls["brand"]["logo"],
	}


def check_css(css: str | None, label: str) -> None:
	"""CSS is placed inside a <style> element, so it must not be able to close it."""
	if css and "</" in css:
		frappe.throw(_("{0} cannot contain {1}.").format(label, "<code>&lt;/</code>"))


def validate_layout(template: str, css: str | None) -> None:
	"""Save-time checks for a custom layout: size, CSS, and a real render with the current settings."""
	if len(template or "") > MAX_TEMPLATE_SIZE:
		frappe.throw(_("The template is larger than {0} KB.").format(MAX_TEMPLATE_SIZE // 1000))
	if len(css or "") > MAX_CSS_SIZE:
		frappe.throw(_("The CSS is larger than {0} KB.").format(MAX_CSS_SIZE // 1000))
	check_css(css, _("CSS"))

	settings = frappe.get_single("Login Studio Settings")
	# Exercise the optional branches too, so a typo inside {% if ls.versions %} is caught now
	settings.tagline = settings.tagline or "Tagline"
	settings.show_versions = 1
	try:
		html = render_layout(template, build_layout_context(settings))
	except TemplateSyntaxError as e:
		frappe.throw(_("Template syntax error on line {0}: {1}").format(e.lineno, escape(e.message)))
	except Exception as e:
		frappe.throw(_("The template failed to render: {0}").format(escape(str(e))))

	if html.count(FORM_TOKEN) != 1:
		frappe.throw(_("The template must output {0} exactly once.").format("<code>{{ login_form }}</code>"))


def build_layout_context(settings, stock_logo: str | None = None) -> dict:
	"""The ``ls`` object available to layout templates. String values are HTML-escaped."""
	lang = frappe.local.lang or "en"
	logo = settings.logo or stock_logo
	show_powered_by = bool(settings.show_powered_by and settings.powered_by_text)
	powered_by_url = settings.powered_by_url if branding.is_http_url(settings.powered_by_url) else None

	return {
		"brand": {
			"name": escape(branding.get_brand_name(settings)),
			"tagline": escape(settings.tagline or ""),
			"logo": escape(logo) if logo else "",
			"background": escape(settings.background_image or ""),
		},
		"powered_by": {
			"show": show_powered_by,
			"text": escape(settings.powered_by_text or ""),
			"url": escape(powered_by_url) if powered_by_url else "",
		},
		"versions": [
			{key: escape(value) for key, value in row.items()}
			for row in (branding.get_app_versions(settings.version_apps) if settings.show_versions else [])
		],
		"lang": escape(lang),
		"dir": branding.text_direction(lang),
	}


def render_layout(template: str, ls: dict) -> str:
	"""Render a layout in Frappe's Jinja sandbox.

	Not ``frappe.render_template``: on error it calls ``frappe.throw`` with the
	template source and traceback, which must never reach a guest page.
	"""
	if ".__" in template:
		raise ValueError("Illegal template")

	partials = Partials(ls)
	template_context = {
		"ls": ls,
		"login_form": Markup(FORM_TOKEN),
		"ls_logo": partials.logo,
		"ls_powered_by": partials.powered_by,
		"ls_versions": partials.versions,
		"ls_background": partials.background,
	}
	with safe_render_flags():
		return get_jenv().from_string(template).render(template_context)


class Partials:
	"""Ready-made HTML pieces that layout templates call as ``{{ ls_logo() }}`` etc."""

	def __init__(self, ls: dict):
		self.ls = ls

	def logo(self, css_class: str = "ls-logo") -> Markup:
		brand = self.ls["brand"]
		if not brand["logo"]:
			return Markup("")
		return Markup('<img class="{}" src="{}" alt="{}">').format(css_class, brand["logo"], brand["name"])

	def powered_by(self) -> Markup:
		powered_by = self.ls["powered_by"]
		if not powered_by["show"]:
			return Markup("")
		text = powered_by["text"]
		if powered_by["url"]:
			text = Markup('<a href="{}" target="_blank" rel="noopener">{}</a>').format(
				powered_by["url"], text
			)
		return Markup('<p class="ls-powered-by">{} {}</p>').format(frappe._("Powered by"), text)

	def versions(self) -> Markup:
		if not self.ls["versions"]:
			return Markup("")
		items = Markup("").join(
			Markup(
				'<li><span class="ls-version__app">{}</span> <span class="ls-version__number">v{}</span></li>'
			).format(row["label"], row["version"])
			for row in self.ls["versions"]
		)
		return Markup('<ul class="ls-versions" aria-label="{}">{}</ul>').format(
			frappe._("App versions"), items
		)

	def background(self) -> Markup:
		if self.ls["brand"]["background"]:
			return Markup('<img class="ls-bg ls-bg--photo" src="{}" alt="" aria-hidden="true">').format(
				self.ls["brand"]["background"]
			)
		return Markup(read_asset("background.svg"))


def build_css(settings, layout) -> str:
	primary = branding.normalize_hex(settings.primary_color, branding.DEFAULT_COLORS["primary"])
	secondary = branding.normalize_hex(settings.secondary_color, branding.DEFAULT_COLORS["secondary"])
	accent = branding.normalize_hex(settings.accent_color, branding.DEFAULT_COLORS["accent"])
	variables = {
		"--ls-primary": primary,
		"--ls-secondary": secondary,
		"--ls-accent": accent,
		"--ls-on-primary": branding.readable_text_on(primary),
		"--ls-radius": branding.RADIUS.get(settings.corner_radius, branding.RADIUS["Medium"]),
		"--ls-font": branding.FONTS.get(settings.font_family, branding.FONTS["Inter"]),
		"--ls-heading-font": branding.HEADING_FONTS.get(
			settings.heading_font, branding.HEADING_FONTS["Same as Font"]
		),
	}
	root = ":root{" + "".join(f"{name}:{value};" for name, value in variables.items()) + "}"
	# </ is rejected on save; dropping it here too keeps a hand-edited DB value from closing <style>
	parts = [root, read_asset("base.css"), layout.css or "", settings.custom_css or ""]
	return "\n".join(part.replace("</", "<\\/") for part in parts)


SHARED_ASSETS = ("base.css", "background.svg")


def read_asset(filename: str) -> str:
	"""Shared files next to the layout folders. Small, read per request."""
	if filename not in SHARED_ASSETS:
		raise ValueError(f"Unknown Login Studio asset: {filename}")
	return frappe.read_file(os.path.join(STANDARD_LAYOUTS_PATH, filename), raise_not_found=True)


def log_render_error() -> None:
	# expires=True: on v15 a plain get_value caches the miss in frappe.local.cache, hiding the setex below
	if frappe.cache.get_value(ERROR_LOG_CACHE_KEY, expires=True):
		return
	frappe.cache.set_value(ERROR_LOG_CACHE_KEY, 1, expires_in_sec=ERROR_LOG_INTERVAL)
	frappe.log_error(title="Login Studio: layout render failed")
