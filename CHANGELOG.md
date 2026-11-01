# Changelog

All notable changes to Login Studio are listed here. The project follows [Semantic Versioning](https://semver.org/); the public plugin API (`login_studio.api` and the `login_studio_*` hooks) only changes incompatibly in a new major version.

## [0.1.0] - 2026-11-01

First release. Supports Frappe / ERPNext v15 and v16.

### Added

- `/login` override that wraps the stock Frappe sign-in form, so password, OTP / 2FA, LDAP, social login, login with email link, forgot password and signup keep working.
- Five predefined, responsive layouts: Split Hero, Centered Card, Glass, Minimal, Corporate Sidebar.
- Login Studio Settings: brand name, tagline, logo, background image, primary / secondary / accent colors, corner radius, font (bundled Inter or system UI) and heading font (bundled Source Serif 4), Powered by text / URL / visibility, app versions (off by default), custom CSS.
- Custom layouts: duplicate any layout and edit its Jinja template and CSS in Desk. Templates are rendered once on save, so syntax and render errors are refused before they reach the login page. Preview at 1440 / 768 / 375 px for System Managers.
- Plugin API: `login_studio_layouts`, `login_studio_context`, `login_studio_slots` and `login_studio_assets` hooks, the `login_studio.api` module, and an example plugin app.
- Optional language switcher that remembers the visitor's choice; Indonesian translation; right-to-left layouts.
- Safety: any layout or plugin error falls back to the stock login and is logged at most once every 5 minutes; `login_studio_disabled` site config kill switch; layout CSS cannot close its `<style>` element; no JavaScript is stored in the database.
- Docs: [layout contract](docs/layout-contract.md) and [plugin guide](docs/plugins.md).

[0.1.0]: https://github.com/thinkspedia/login_studio/releases/tag/v0.1.0
