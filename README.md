<div align="center">

# Login Studio

**Professional, configurable and pluggable login pages for Frappe & ERPNext.**

Pick a layout, apply your brand, edit HTML/CSS live — no `bench build`, no forks of core.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Frappe](https://img.shields.io/badge/Frappe-v15%20%7C%20v16-0089FF)
![ERPNext](https://img.shields.io/badge/ERPNext-v15%20%7C%20v16-0089FF)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)
![Status](https://img.shields.io/badge/status-in%20development-orange)

</div>

> [!WARNING]
> Login Studio is **under active development** and has not had its first release yet.
> The features below describe the v0.1.0 scope. Do not install it on production sites until a tagged release is published.

---

## Why Login Studio?

Frappe's default `/login` page is a plain card with a small logo. Changing it today usually means editing core files (lost on every update), copying the whole login template into a custom app (breaks when upstream changes OTP, LDAP or social login), or fragile CSS hacks.

Login Studio replaces all of that with one installable app:

- **Wraps, never copies, the stock login form.** Password, OTP / 2FA, LDAP, social login, login-with-email-link, forgot password and signup keep working — and keep receiving upstream fixes.
- **Never locks you out.** Any layout or plugin error falls back to the stock Frappe login automatically, and a site-config kill switch is always available.

## Features (v0.1.0 scope)

| | |
|---|---|
| **Predefined layouts** | Split Hero, Centered Card, Glass, Minimal, Corporate Sidebar — mobile-first and responsive from 320 px up |
| **Branding** | Logo (light/dark), brand name, tagline, background image, primary / secondary / accent colors, fonts, corner radius |
| **Powered by** | Configurable text and URL, show or hide |
| **App versions** | Optionally show Frappe / ERPNext / HRMS (or any installed app) versions — off by default |
| **Live custom layouts** | Duplicate any layout and edit its HTML (Jinja) and CSS in Desk; changes are live on save |
| **Layout contract** | Documented variables, macros and CSS custom properties so custom layouts stay safe and upgrade-proof |
| **Languages** | Follows the visitor's browser language, with an optional on-page language switcher; RTL-ready |
| **Plugin API** | Other apps can add layouts, context data, page slots and assets through `hooks.py` — no changes to Login Studio needed |
| **On / off** | One checkbox restores the exact stock Frappe login |
| **Privacy** | Fonts bundled locally; no third-party CDN calls from the login page by default |

## Compatibility

| Frappe / ERPNext | Branch | Python |
|---|---|---|
| v16 | `version-16` | 3.14 |
| v15 | `version-15` | 3.10+ |

ERPNext and HRMS are optional — Login Studio only requires Frappe.

## Installation

Available once v0.1.0 is released.

```bash
# Pick the branch that matches your Frappe version
bench get-app https://github.com/thinkspedia/login_studio --branch version-16
bench --site your-site.com install-app login_studio
```

Then open **Login Studio Settings** in Desk, choose a layout and set your branding.

### Emergency switch

If a custom layout ever misbehaves, disable Login Studio without touching the database:

```bash
bench --site your-site.com set-config login_studio_disabled 1
```

## Custom layouts at a glance

A layout is a Jinja template plus CSS. The only required piece is the stock login form:

```jinja
<main class="my-login">
  <aside class="my-login__brand">
    {{ ls_logo() }}
    <h1>{{ ls.brand.name }}</h1>
    <p>{{ ls.brand.tagline }}</p>
  </aside>
  <section class="my-login__form">
    {{ login_form }}
    {{ ls_powered_by() }}
  </section>
</main>
```

```css
.my-login { display: grid; min-height: 100vh; grid-template-columns: 1fr; }
.my-login__brand { background: linear-gradient(135deg, var(--ls-primary), var(--ls-secondary)); color: var(--ls-on-primary); }
@media (min-width: 992px) { .my-login { grid-template-columns: 1fr 1fr; } }
```

The full layout contract (variables, macros, CSS custom properties) will be documented in `docs/layout-contract.md`.

## Plugin API at a glance

Extend Login Studio from your own app's `hooks.py`:

```python
login_studio_layouts = ["my_app/login_layouts"]           # ship extra layouts
login_studio_context = ["my_app.login.add_context"]       # add data to the template
login_studio_slots = {"below_form": "my_app.login.notice"}  # inject HTML into named slots
login_studio_assets = {"css": ["/assets/my_app/css/login.css"]}
```

The plugin guide will be documented in `docs/plugins.md`.

## Roadmap

- [ ] App scaffold, CI on Frappe v15 and v16
- [ ] Core: settings, safe rendering, fallback, Split Hero layout
- [ ] Remaining predefined layouts
- [ ] Custom layouts with validation and live preview
- [ ] Plugin API and example plugin
- [ ] Translations (English, Indonesian) and language switcher
- [ ] v0.1.0 release and Frappe Cloud Marketplace listing

## Development

```bash
cd frappe-bench
bench get-app https://github.com/thinkspedia/login_studio --branch develop
bench --site dev.localhost install-app login_studio

cd apps/login_studio
pre-commit install          # ruff, prettier, eslint on every commit

bench --site dev.localhost set-config allow_tests true
bench --site dev.localhost run-tests --app login_studio
```

Code must stay **Python 3.10 compatible** (Frappe v15). Anything that differs between Frappe v15 and v16 belongs in `login_studio/compat.py`. CI runs every test on both versions.

## Contributing

Issues and pull requests are welcome once the repository is public. Please open an issue to discuss larger changes first. New layouts, translations and plugins are especially appreciated.

## Security

Please do not report security issues in public issues. Use GitHub's **[private vulnerability reporting](https://github.com/thinkspedia/login_studio/security/advisories/new)** instead.

## License

[MIT](LICENSE) © 2026 [Thinkspedia](https://thinkspedia.id)

### Third-party fonts

Bundled unmodified under the SIL Open Font License 1.1, license files next to each font:

- [Inter](https://github.com/rsms/inter) v4.1, © The Inter Project Authors — `login_studio/public/fonts/inter/`
- [Source Serif 4](https://github.com/adobe-fonts/source-serif) 4.005, © Adobe — `login_studio/public/fonts/source-serif-4/`

---

<div align="center">

Built and maintained by **[Thinkspedia](https://thinkspedia.id)** — proud contributors to the Frappe and ERPNext community.

</div>
