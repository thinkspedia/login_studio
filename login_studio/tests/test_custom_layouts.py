import importlib.util
import os

import frappe

from login_studio import render
from login_studio.login_studio.doctype.login_layout.login_layout import duplicate_layout
from login_studio.tests.utils import IntegrationTestCase

COPY = "test_custom_copy"


def load_preview_module():
	# The route folder is "login-studio", which is not an importable package name
	# (get_app_path would also scrub the hyphen, so join it by hand)
	path = os.path.join(frappe.get_app_path("login_studio", "www"), "login-studio", "preview.py")
	spec = importlib.util.spec_from_file_location("login_studio_preview_page", path)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module


class TestCustomLayouts(IntegrationTestCase):
	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.form_dict.pop("layout", None)
		settings = frappe.get_single("Login Studio Settings")
		if settings.active_layout == COPY or settings.custom_css:
			settings.active_layout = "split_hero"
			settings.custom_css = ""
			settings.save()
		if frappe.db.exists("Login Layout", COPY):
			frappe.delete_doc("Login Layout", COPY, force=True)

	def new_layout(self, template="{{ login_form }}", css="", name=COPY):
		return frappe.get_doc(
			{
				"doctype": "Login Layout",
				"layout_name": name,
				"title": "Copy",
				"template": template,
				"css": css,
			}
		)

	def test_duplicate_creates_editable_custom_copy(self):
		name = duplicate_layout("split_hero", COPY, "My Split")
		copy = frappe.get_doc("Login Layout", name)
		self.assertEqual(copy.source, "Custom")
		self.assertIsNone(copy.source_app)
		self.assertEqual(copy.based_on, "split_hero")
		self.assertEqual(copy.template, frappe.db.get_value("Login Layout", "split_hero", "template"))

		copy.css += "\n.ls-split { outline: 1px solid red; }"
		copy.save()

	def test_layouts_made_in_desk_are_always_custom(self):
		layout = self.new_layout()
		layout.source = "Standard"
		layout.source_app = "login_studio"
		layout.insert()
		self.assertEqual(layout.source, "Custom")
		self.assertIsNone(layout.source_app)

	def test_rejects_broken_templates(self):
		cases = {
			"syntax error": "{{ login_form }}{% if %}",
			"render error": "{{ login_form }}{{ 1 / 0 }}",
			"no form": "{# login_form #}<div></div>",
			"form twice": "{{ login_form }}{{ login_form }}",
			"error in optional branch": "{{ login_form }}{% if ls.versions %}{{ 1 / 0 }}{% endif %}",
			"sandbox escape": "{{ login_form }}{{ ls.__class__ }}",
		}
		for label, template in cases.items():
			with self.subTest(label):
				self.assertRaises(frappe.ValidationError, self.new_layout(template).insert)

	def test_rejects_css_that_closes_the_style_tag(self):
		layout = self.new_layout(css="a{color:red}</style><script>alert(1)</script>")
		self.assertRaises(frappe.ValidationError, layout.insert)

	def test_size_limits(self):
		big_template = "{{ login_form }}" + "<p></p>" * (render.MAX_TEMPLATE_SIZE // 7 + 1)
		self.assertRaises(frappe.ValidationError, self.new_layout(big_template).insert)
		big_css = "a{}" * (render.MAX_CSS_SIZE // 3 + 1)
		self.assertRaises(frappe.ValidationError, self.new_layout(css=big_css).insert)

	def test_layout_name_format(self):
		for bad in ("Has Space", "UPPER", "_underscore_first", "dash-name"):
			with self.subTest(bad):
				self.assertRaises(frappe.ValidationError, self.new_layout(name=bad).insert)

	def test_active_layout_cannot_be_deleted(self):
		self.new_layout().insert()
		settings = frappe.get_single("Login Studio Settings")
		settings.active_layout = COPY
		settings.save()
		self.assertRaises(frappe.ValidationError, frappe.delete_doc, "Login Layout", COPY)

	def test_standard_layout_cannot_be_deleted(self):
		self.assertRaises(frappe.ValidationError, frappe.delete_doc, "Login Layout", "minimal")

	def test_custom_css_is_appended_and_checked(self):
		settings = frappe.get_single("Login Studio Settings")
		settings.custom_css = ".ls-root { letter-spacing: 0.01em; }"
		settings.save()
		css = render.build_css(settings, frappe.get_doc("Login Layout", "split_hero"))
		self.assertTrue(css.rstrip().endswith(".ls-root { letter-spacing: 0.01em; }"))

		settings.custom_css = "</style><script>x()</script>"
		self.assertRaises(frappe.ValidationError, settings.save)

	def test_css_cannot_close_style_tag_even_if_stored(self):
		settings = frappe.get_single("Login Studio Settings")
		settings.custom_css = "a{}</style><script>x()</script>"
		css = render.build_css(settings, frappe.get_doc("Login Layout", "split_hero"))
		self.assertNotIn("</style", css)


class TestPreviewPage(IntegrationTestCase):
	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.form_dict.pop("layout", None)

	def test_guest_cannot_preview(self):
		frappe.set_user("Guest")
		frappe.form_dict.layout = "split_hero"
		self.assertRaises(frappe.PermissionError, load_preview_module().get_context, frappe._dict())

	def test_preview_renders_any_layout_even_when_disabled(self):
		frappe.db.set_value("Login Layout", "glass", "enabled", 0)
		try:
			frappe.form_dict.layout = "glass"
			context = load_preview_module().get_context(frappe._dict())
			self.assertIn("ls-glass", context.ls["before"])
		finally:
			frappe.db.set_value("Login Layout", "glass", "enabled", 1)

	def test_preview_shows_render_errors(self):
		frappe.get_doc(
			{"doctype": "Login Layout", "layout_name": COPY, "title": "Copy", "template": "{{ login_form }}"}
		).insert()
		frappe.db.set_value("Login Layout", COPY, "template", "{{ login_form }}{{ 1 / 0 }}")
		try:
			frappe.form_dict.layout = COPY
			context = load_preview_module().get_context(frappe._dict())
			self.assertIsNone(context.ls)
			self.assertIn("division by zero", context.preview_error)
		finally:
			frappe.delete_doc("Login Layout", COPY, force=True)
