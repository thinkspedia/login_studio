import unittest
from contextlib import contextmanager
from unittest.mock import patch

import frappe

from login_studio import api, render
from login_studio.layouts import get_layout_sources, remove_app_layouts, sync_layouts
from login_studio.tests.utils import IntegrationTestCase

EXAMPLE_APP = "login_studio_plugin_example"
real_get_hooks = frappe.get_hooks


# Hook functions used by the tests below (referenced by dotted path)
def add_extra(ls):
	ls["extra"]["greeting"] = "hello"


def greeting_slot(ls):
	return f"<b class='test-slot'>{ls['extra'].get('greeting', '')}</b>"


def broken_hook(ls):
	raise RuntimeError("plugin bug")


@contextmanager
def fake_hooks(**hooks):
	"""Pretend installed apps declare ``hooks``; every other hook is the real one."""

	def get_hooks(hook=None, *args, **kwargs):
		if hook in hooks:
			return hooks[hook]
		# Pass arguments through untouched: newer Frappe uses a sentinel default, not None
		return real_get_hooks(hook, *args, **kwargs)

	with patch("frappe.get_hooks", side_effect=get_hooks):
		yield


class TestPluginHooks(IntegrationTestCase):
	def setUp(self):
		for path in ("broken_hook",):
			frappe.cache.delete_value(f"login_studio:hook_error:{__name__}.{path}")
		self.settings = frappe.get_single("Login Studio Settings")
		self.layout = frappe.get_doc("Login Layout", "split_hero")

	def render_page(self):
		return render.build_page(self.settings, self.layout)

	def test_context_hook_and_slot(self):
		with fake_hooks(
			login_studio_context=[f"{__name__}.add_extra"],
			login_studio_slots={"below_form": [f"{__name__}.greeting_slot"]},
		):
			page = self.render_page()
		self.assertIn("<b class='test-slot'>hello</b>", page["after"])
		self.assertIn("ls-slot--below_form", page["after"])

	def test_every_standard_layout_offers_the_slots(self):
		slots = {name: [f"{__name__}.greeting_slot"] for name in render.SLOT_NAMES}
		with fake_hooks(login_studio_context=[f"{__name__}.add_extra"], login_studio_slots=slots):
			ls = render.build_layout_context(self.settings)
			for layout in ("split_hero", "centered_card", "glass", "minimal", "corporate_sidebar"):
				html = render.render_layout(frappe.get_doc("Login Layout", layout).template, ls)
				for slot in render.SLOT_NAMES:
					with self.subTest(layout=layout, slot=slot):
						self.assertIn(f"ls-slot--{slot}", html)

	def test_unknown_slot_is_ignored(self):
		with fake_hooks(login_studio_slots={"sidebar_ad": [f"{__name__}.greeting_slot"]}):
			ls = render.build_layout_context(self.settings)
		self.assertEqual(ls["slots"], {})

	def test_failing_hook_is_skipped_and_logged_once(self):
		before = frappe.db.count("Error Log")
		with fake_hooks(
			login_studio_context=[f"{__name__}.broken_hook", f"{__name__}.add_extra"],
			login_studio_slots={
				"footer": [f"{__name__}.broken_hook"],
				"below_form": [f"{__name__}.greeting_slot"],
			},
		):
			page = self.render_page()
			self.render_page()
		self.assertIn("hello", page["after"])
		self.assertNotIn("ls-slot--footer", page["after"])
		self.assertEqual(frappe.db.count("Error Log"), before + 1)

	def test_assets_only_same_site_or_https(self):
		assets = {
			"css": ["/assets/x/a.css", "https://cdn.example.com/b.css", "http://plain.example.com/c.css"],
			"js": ["//evil.example.com/d.js", "javascript:alert(1)", '/assets/x/e.js"onload="x()'],
		}
		with fake_hooks(login_studio_assets=assets):
			result = self.render_page()["assets"]
		self.assertEqual(result["css"], ["/assets/x/a.css", "https://cdn.example.com/b.css"])
		self.assertEqual(len(result["js"]), 1)
		self.assertNotIn('"', result["js"][0])

	def test_layout_folders_must_stay_inside_the_app(self):
		def hooks_for(hook=None, *args, **kwargs):
			if hook == "login_studio_layouts":
				return {"frappe": ["www", "../../../etc", "does_not_exist"]}.get(kwargs.get("app_name"), [])
			return real_get_hooks(hook, *args, **kwargs)

		with patch("frappe.get_hooks", side_effect=hooks_for):
			sources = get_layout_sources("frappe")
		self.assertEqual([(s, a) for s, a, _ in sources], [("Plugin", "frappe")])
		self.assertTrue(sources[0][2].endswith("/frappe/www"))

	def test_public_api(self):
		self.assertEqual(api.SLOT_NAMES, ("hero", "above_form", "below_form", "footer"))
		page = api.render_layout("minimal")
		self.assertEqual(set(page), {"before", "after", "css", "assets"})
		self.assertIn("brand", api.get_layout_context())


@unittest.skipUnless(
	EXAMPLE_APP in frappe.get_installed_apps() if frappe.db else False,
	"login_studio_plugin_example is not installed",
)
class TestExamplePlugin(IntegrationTestCase):
	def tearDown(self):
		sync_layouts(EXAMPLE_APP)
		settings = frappe.get_single("Login Studio Settings")
		if settings.active_layout != "split_hero":
			settings.active_layout = "split_hero"
			settings.save()

	def test_layout_is_synced_as_plugin(self):
		layout = frappe.get_doc("Login Layout", "lspe_aurora")
		self.assertEqual((layout.source, layout.source_app), ("Plugin", EXAMPLE_APP))
		layout.css += "a{}"
		self.assertRaises(frappe.ValidationError, layout.save)

	def test_page_uses_layout_slot_and_asset(self):
		settings = frappe.get_single("Login Studio Settings")
		settings.active_layout = "lspe_aurora"
		settings.save()
		page = render.get_page_context(frappe._dict())
		self.assertIn("lspe-aurora", page["before"])
		self.assertIn("support@example.com", page["after"])
		self.assertIn(
			"/assets/login_studio_plugin_example/css/login_studio_plugin_example.css", page["assets"]["css"]
		)

	def test_uninstall_removes_layouts_and_resets_active(self):
		frappe.db.set_single_value("Login Studio Settings", "active_layout", "lspe_aurora")
		remove_app_layouts(EXAMPLE_APP)
		self.assertFalse(frappe.db.exists("Login Layout", "lspe_aurora"))
		self.assertEqual(frappe.db.get_single_value("Login Studio Settings", "active_layout"), "split_hero")
