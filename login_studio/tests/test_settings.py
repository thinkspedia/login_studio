import frappe

from login_studio.tests.utils import IntegrationTestCase


class TestLoginStudioSettings(IntegrationTestCase):
	def get_settings(self):
		return frappe.get_single("Login Studio Settings")

	def test_install_defaults(self):
		settings = self.get_settings()
		self.assertEqual(settings.active_layout, "split_hero")
		self.assertEqual(settings.powered_by_text, "Thinkspedia")
		self.assertEqual(settings.powered_by_url, "https://thinkspedia.id")
		self.assertEqual(settings.show_versions, 0)

	def test_rejects_invalid_color(self):
		settings = self.get_settings()
		settings.primary_color = "blue"
		self.assertRaises(frappe.ValidationError, settings.save)

	def test_rejects_non_http_powered_by_url(self):
		settings = self.get_settings()
		settings.powered_by_url = "javascript:alert(1)"
		self.assertRaises(frappe.ValidationError, settings.save)

	def test_rejects_disabled_active_layout(self):
		frappe.db.set_value("Login Layout", "split_hero", "enabled", 0)
		try:
			settings = self.get_settings()
			settings.enabled = 1
			settings.active_layout = "split_hero"
			self.assertRaises(frappe.ValidationError, settings.save)
		finally:
			frappe.db.set_value("Login Layout", "split_hero", "enabled", 1)
