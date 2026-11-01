import frappe

from login_studio import render
from login_studio.layouts import get_standard_layout_names, sync_standard_layouts
from login_studio.tests.utils import IntegrationTestCase

TEST_LAYOUT = "test_login_studio_layout"


class TestRender(IntegrationTestCase):
	def setUp(self):
		frappe.cache.delete_value(render.ERROR_LOG_CACHE_KEY)
		frappe.local.conf.pop("login_studio_disabled", None)
		self.settings = frappe.get_single("Login Studio Settings")
		self.original = self.settings.as_dict()

	def tearDown(self):
		frappe.local.conf.pop("login_studio_disabled", None)
		settings = frappe.get_single("Login Studio Settings")
		for field in (
			"enabled",
			"active_layout",
			"brand_name",
			"tagline",
			"show_versions",
			"show_powered_by",
		):
			settings.set(field, self.original.get(field))
		settings.save()
		if frappe.db.exists("Login Layout", TEST_LAYOUT):
			frappe.delete_doc("Login Layout", TEST_LAYOUT, force=True)

	def update_settings(self, **values):
		self.settings.update(values)
		self.settings.save()

	def use_custom_layout(self, template):
		"""Activate a custom layout with ``template`` written straight to the DB: broken templates are
		rejected on save, but the page must still survive one that got there anyway."""
		layout = frappe.get_doc(
			{
				"doctype": "Login Layout",
				"layout_name": TEST_LAYOUT,
				"title": "Test",
				"template": "{{ login_form }}",
			}
		).insert()
		self.update_settings(enabled=1, active_layout=layout.name)
		frappe.db.set_value("Login Layout", TEST_LAYOUT, "template", template)
		frappe.clear_document_cache("Login Layout", TEST_LAYOUT)

	def test_renders_active_layout_around_the_form(self):
		self.update_settings(enabled=1, active_layout="split_hero", brand_name="Acme")
		ls = render.get_page_context(frappe._dict(logo="/files/logo.png"))
		self.assertIsNotNone(ls)
		self.assertIn("ls-split", ls["before"])
		self.assertIn("Acme", ls["before"])
		self.assertNotIn(render.FORM_TOKEN, ls["before"] + ls["after"])
		self.assertIn("--ls-primary", ls["css"])
		self.assertEqual(ls["logo"], "/files/logo.png")

	def test_disabled_renders_stock_login(self):
		self.update_settings(enabled=0)
		self.assertIsNone(render.get_page_context(frappe._dict()))

	def test_site_config_kill_switch(self):
		self.update_settings(enabled=1, active_layout="split_hero")
		frappe.local.conf.login_studio_disabled = 1
		self.assertIsNone(render.get_page_context(frappe._dict()))

	def test_brand_values_are_escaped(self):
		# Built from an in-memory doc: Frappe already strips <script> from Data fields on save
		settings = frappe.get_single("Login Studio Settings")
		settings.brand_name = "<script>x()</script>"
		settings.tagline = '"><img src=x onerror=y()>'
		ls = render.build_layout_context(settings)
		html = render.render_layout(frappe.get_doc("Login Layout", "split_hero").template, ls)
		self.assertNotIn("<script>x()", html)
		self.assertIn("&lt;script&gt;", html)
		self.assertNotIn("<img src=x", html)

	def test_powered_by_and_versions_follow_settings(self):
		self.update_settings(enabled=1, active_layout="split_hero", show_powered_by=1, show_versions=0)
		html = str(render.get_page_context(frappe._dict())["after"])
		self.assertIn("ls-powered-by", html)
		self.assertNotIn("ls-versions", html)

		self.update_settings(show_powered_by=0, show_versions=1)
		html = str(render.get_page_context(frappe._dict())["after"])
		self.assertNotIn("ls-powered-by", html)
		self.assertIn("ls-versions", html)

	def test_render_error_falls_back_and_logs_once(self):
		self.use_custom_layout("{{ login_form }}{{ 1 / 0 }}")
		before = frappe.db.count("Error Log")
		self.assertIsNone(render.get_page_context(frappe._dict()))
		self.assertIsNone(render.get_page_context(frappe._dict()))
		self.assertEqual(frappe.db.count("Error Log"), before + 1)

	def test_layout_must_output_the_form_once(self):
		self.use_custom_layout("{# login_form #}<div>no form</div>")
		self.assertIsNone(render.get_page_context(frappe._dict()))

		self.update_settings(active_layout="split_hero")
		frappe.delete_doc("Login Layout", TEST_LAYOUT, force=True)
		self.use_custom_layout("{{ login_form }}{{ login_form }}")
		self.assertIsNone(render.get_page_context(frappe._dict()))

	def test_sandbox_blocks_dunder_access(self):
		self.use_custom_layout("{{ login_form }}{{ ls.__class__ }}")
		self.assertIsNone(render.get_page_context(frappe._dict()))


class TestLayouts(IntegrationTestCase):
	def test_standard_layouts_are_synced(self):
		names = get_standard_layout_names()
		self.assertIn("split_hero", names)
		sync_standard_layouts()
		for name in names:
			self.assertEqual(frappe.db.get_value("Login Layout", name, "source"), "Standard")

	def test_every_standard_layout_renders(self):
		settings = frappe.get_single("Login Studio Settings")
		settings.brand_name = "Acme & Co"
		settings.tagline = "Tagline"
		settings.show_versions = 1
		ls = render.build_layout_context(settings, stock_logo="/files/logo.png")
		for name in get_standard_layout_names():
			with self.subTest(layout=name):
				html = render.render_layout(frappe.get_doc("Login Layout", name).template, ls)
				self.assertEqual(html.count(render.FORM_TOKEN), 1)
				self.assertIn("Acme &amp; Co", html)
				self.assertIn("ls-versions", html)
				self.assertIn('class="ls-root', html)

	def test_font_settings_set_css_variables(self):
		settings = frappe.get_single("Login Studio Settings")
		layout = frappe.get_doc("Login Layout", "split_hero")
		settings.font_family = "System UI"
		settings.heading_font = "Source Serif"
		css = render.build_css(settings, layout)
		self.assertIn("--ls-font:system-ui", css)
		self.assertIn('--ls-heading-font:"Login Studio Source Serif"', css)

		settings.font_family = None
		self.assertIn('--ls-font:"Login Studio Inter"', render.build_css(settings, layout))

	def test_sync_keeps_enabled_flag(self):
		frappe.db.set_value("Login Layout", "split_hero", "enabled", 0)
		sync_standard_layouts()
		self.assertEqual(frappe.db.get_value("Login Layout", "split_hero", "enabled"), 0)
		frappe.db.set_value("Login Layout", "split_hero", "enabled", 1)

	def test_standard_layout_cannot_be_edited(self):
		layout = frappe.get_doc("Login Layout", "split_hero")
		layout.template = layout.template + "<p>changed</p>"
		self.assertRaises(frappe.ValidationError, layout.save)

	def test_custom_layout_requires_login_form(self):
		layout = frappe.get_doc(
			{
				"doctype": "Login Layout",
				"layout_name": TEST_LAYOUT,
				"title": "Test",
				"template": "<div></div>",
			}
		)
		self.assertRaises(frappe.ValidationError, layout.insert)
