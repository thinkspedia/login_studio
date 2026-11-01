from unittest.mock import MagicMock, patch

import frappe
from frappe.translate import get_all_translations

from login_studio import render
from login_studio.tests.utils import IntegrationTestCase


class TestLanguageSwitcher(IntegrationTestCase):
	def setUp(self):
		for code in ("id", "ar"):
			frappe.db.set_value("Language", code, "enabled", 1)
		self.settings = frappe.get_single("Login Studio Settings")

	def tearDown(self):
		frappe.form_dict.pop("_lang", None)
		settings = frappe.get_single("Login Studio Settings")
		settings.show_language_switcher = 0
		settings.languages = []
		settings.save()

	def enable_switcher(self, *codes):
		self.settings.show_language_switcher = 1
		self.settings.languages = []
		for code in codes:
			self.settings.append("languages", {"language": code})
		self.settings.save()

	def test_off_by_default(self):
		self.assertEqual(render.get_switcher_languages(self.settings, "en"), [])
		ls = render.build_layout_context(self.settings)
		html = render.render_layout(frappe.get_doc("Login Layout", "split_hero").template, ls)
		self.assertNotIn("ls-lang", html)

	def test_languages_in_configured_order_with_current(self):
		self.enable_switcher("id", "en", "ar")
		rows = render.get_switcher_languages(self.settings, "en")
		self.assertEqual([row["code"] for row in rows], ["id", "en", "ar"])
		self.assertEqual([row["current"] for row in rows], [False, True, False])
		self.assertEqual(rows[0]["url"], "?_lang=id")

	def test_disabled_language_is_skipped(self):
		self.enable_switcher("id", "ar")
		frappe.db.set_value("Language", "ar", "enabled", 0)
		self.assertEqual([row["code"] for row in render.get_switcher_languages(self.settings, "en")], ["id"])

	def test_redirect_target_is_kept(self):
		self.enable_switcher("id")
		request = MagicMock()
		request.args = {"redirect-to": "/app/todo?x=1"}
		with patch.object(frappe.local, "request", request, create=True):
			rows = render.get_switcher_languages(self.settings, "en")
		self.assertEqual(rows[0]["url"], "?redirect-to=%2Fapp%2Ftodo%3Fx%3D1&amp;_lang=id")

	def test_every_standard_layout_shows_the_switcher(self):
		self.enable_switcher("en", "id")
		ls = render.build_layout_context(self.settings)
		for name in ("split_hero", "centered_card", "glass", "minimal", "corporate_sidebar"):
			with self.subTest(layout=name):
				html = render.render_layout(frappe.get_doc("Login Layout", name).template, ls)
				self.assertIn('<nav class="ls-lang"', html)
				self.assertIn('hreflang="id"', html)

	def test_switcher_choice_is_remembered_only_for_offered_languages(self):
		self.enable_switcher("id")
		cookie_manager = MagicMock()
		with patch.object(frappe.local, "cookie_manager", cookie_manager, create=True):
			frappe.form_dict._lang = "ar"
			render.remember_language()
			cookie_manager.set_cookie.assert_not_called()

			frappe.form_dict._lang = "id"
			render.remember_language()
			cookie_manager.set_cookie.assert_called_once_with("preferred_language", "id")

	def test_right_to_left_language(self):
		with patch.object(frappe.local, "lang", "ar"):
			ls = render.build_layout_context(self.settings)
		self.assertEqual(ls["dir"], "rtl")


class TestTranslations(IntegrationTestCase):
	def test_indonesian_translations_load(self):
		translations = get_all_translations("id")
		self.assertEqual(translations.get("Login Studio Settings"), "Pengaturan Login Studio")
		self.assertEqual(translations.get("Sign In"), "Masuk")
		self.assertNotIn("Powered by", translations, "Powered by stays as written in every language")
