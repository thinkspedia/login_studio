import frappe

from login_studio.compat import FRAPPE_MAJOR, SUPPORTED_MAJORS, is_supported
from login_studio.tests.utils import IntegrationTestCase


class TestInstall(IntegrationTestCase):
	def test_app_is_installed(self):
		self.assertIn("login_studio", frappe.get_installed_apps())

	def test_running_on_supported_frappe_version(self):
		self.assertTrue(is_supported(), f"Frappe v{FRAPPE_MAJOR} is not in {SUPPORTED_MAJORS}")
