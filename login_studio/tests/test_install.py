import frappe

from login_studio.compat import DESK_PATH, FRAPPE_MAJOR, SUPPORTED_MAJORS, is_supported
from login_studio.tests.utils import IntegrationTestCase


class TestInstall(IntegrationTestCase):
	def test_app_is_installed(self):
		self.assertIn("login_studio", frappe.get_installed_apps())

	def test_running_on_supported_frappe_version(self):
		self.assertTrue(is_supported(), f"Frappe v{FRAPPE_MAJOR} is not in {SUPPORTED_MAJORS}")


class TestAppsScreen(IntegrationTestCase):
	def tearDown(self):
		frappe.set_user("Administrator")

	def login_studio_tile(self):
		from frappe.apps import get_apps

		# v16 caches get_apps per request, which would outlive frappe.set_user here
		getattr(frappe.local, "request_cache", {}).clear()
		return next((app for app in get_apps() if app["name"] == "login_studio"), None)

	def test_tile_opens_the_login_studio_workspace(self):
		tile = self.login_studio_tile()
		self.assertIsNotNone(tile)
		self.assertEqual(tile["route"], f"{DESK_PATH}/login-studio")
		self.assertEqual(tile["logo"], "/assets/login_studio/images/login-studio-logo.svg")

	def test_tile_hidden_from_users_without_system_manager(self):
		frappe.set_user("Guest")
		self.assertIsNone(self.login_studio_tile())
