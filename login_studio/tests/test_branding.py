import frappe

from login_studio import branding
from login_studio.tests.utils import IntegrationTestCase


class TestBranding(IntegrationTestCase):
	def test_readable_text_on_primary(self):
		self.assertEqual(branding.readable_text_on("#4338CA"), branding.LIGHT_TEXT)
		self.assertEqual(branding.readable_text_on("#FDE68A"), branding.DARK_TEXT)

	def test_readable_text_meets_wcag_aa(self):
		for color in ("#4338CA", "#0EA5E9", "#FDE68A", "#16A34A", "#000000", "#FFFFFF"):
			text = branding.readable_text_on(color)
			self.assertGreaterEqual(branding.contrast_ratio(color, text), 4.5, color)

	def test_normalize_hex(self):
		self.assertEqual(branding.normalize_hex("#abc", "#000000"), "#AABBCC")
		self.assertEqual(branding.normalize_hex("#4338ca", "#000000"), "#4338CA")
		self.assertEqual(branding.normalize_hex("red", "#000000"), "#000000")
		self.assertEqual(branding.normalize_hex(None, "#000000"), "#000000")

	def test_http_url(self):
		self.assertTrue(branding.is_http_url("https://thinkspedia.id"))
		self.assertFalse(branding.is_http_url("javascript:alert(1)"))
		self.assertFalse(branding.is_http_url(""))

	def test_text_direction(self):
		self.assertEqual(branding.text_direction("ar"), "rtl")
		self.assertEqual(branding.text_direction("id"), "ltr")
		self.assertEqual(branding.text_direction(None), "ltr")

	def test_versions_skip_apps_not_installed(self):
		rows = [frappe._dict(app="frappe", label=""), frappe._dict(app="not_an_installed_app", label="")]
		versions = branding.get_app_versions(rows)
		self.assertEqual([v["app"] for v in versions], ["frappe"])
		self.assertEqual(versions[0]["version"], frappe.__version__)

	def test_versions_default_list(self):
		apps = [v["app"] for v in branding.get_app_versions([])]
		self.assertIn("frappe", apps)
		for app in apps:
			self.assertIn(app, branding.DEFAULT_VERSION_APPS)
