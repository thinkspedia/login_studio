# Layout contract

A Login Studio layout is a Jinja template plus CSS. This page lists everything a template can use and the rules it must follow. The five built-in layouts in `login_studio/layouts/` follow the same contract and are good starting points.

## Making a custom layout

1. Open **Login Layout** in Desk, pick any layout and click **Duplicate as Custom Layout**.
2. Edit **Template** and **CSS**, then save. Saving renders the template once with your current settings; any error is shown and the layout is not saved.
3. Click **Preview** to see it at 1440, 768 and 375 px. The preview uses a sample form, because the real `/login` page redirects signed-in users away.
4. Select it as **Active Layout** in **Login Studio Settings**. The change is live immediately: no `bench build`, no restart.

Built-in (Standard) layouts and layouts shipped by other apps (Plugin) are read-only; duplicate them to customize.

## Rules

- The template must output `{{ login_form }}` **exactly once**. That is where Frappe's own sign-in form goes, unchanged, so password, OTP/2FA, LDAP, social login, login with email link, forgot password and signup keep working.
- Templates run in Frappe's Jinja sandbox. Attribute names starting with `__` are refused.
- Brand values in `ls` are already HTML-escaped. Print them as they are; do not add `| safe`.
- CSS goes inside a `<style>` element and may not contain `</`.
- JavaScript cannot be stored in a layout. It can only come from an installed app (see the plugin guide), so it goes through code review and deployment.
- Size limits: template 100 KB, CSS 200 KB.
- If a layout ever fails at runtime, visitors get the stock Frappe login and an Error Log entry is written (at most once every 5 minutes).

## Template variables

| Variable | Content |
|---|---|
| `login_form` | **Required.** The stock Frappe sign-in form |
| `ls.brand.name` | Brand Name, falling back to Website Settings app name, the default company, then the site name |
| `ls.brand.tagline` | Tagline (may be empty) |
| `ls.brand.logo` | Logo URL, falling back to the site's app logo (may be empty) |
| `ls.brand.background` | Background Image URL (empty means the built-in illustration) |
| `ls.powered_by.show` | `true` when Show Powered By is on and the text is not empty |
| `ls.powered_by.text`, `ls.powered_by.url` | Powered By text and URL (URL may be empty) |
| `ls.versions` | List of `{app, label, version}`; empty unless Show App Versions is on |
| `ls.lang` | Current language code, e.g. `en`, `id` |
| `ls.dir` | `ltr` or `rtl` |
| `ls.languages` | Switcher entries `{code, name, url, current}`; empty unless Show Language Switcher is on |
| `ls.extra`, `ls.slots` | Data and HTML added by plugins (see the [plugin guide](plugins.md)) |
| `_()` | Translation function: `{{ _("Welcome") }}` |

## Ready-made partials

Call these instead of rebuilding common pieces; they already handle empty values.

| Call | Output |
|---|---|
| `{{ ls_logo() }}` | `<img class="ls-logo">`, or nothing when there is no logo. Optional argument: a CSS class |
| `{{ ls_background() }}` | The uploaded photo, or the built-in SVG illustration tinted with your colors |
| `{{ ls_powered_by() }}` | The Powered by line, or nothing when it is turned off |
| `{{ ls_versions() }}` | Version badges, or nothing when versions are hidden |
| `{{ ls_language_switcher() }}` | Language links, or nothing when the switcher is off |
| `{{ ls_slot("below_form") }}` | Plugin HTML for a slot (`hero`, `above_form`, `below_form`, `footer`), or nothing |

## CSS custom properties

Set on `:root` from Login Studio Settings, before the layout CSS:

| Property | Setting |
|---|---|
| `--ls-primary`, `--ls-secondary`, `--ls-accent` | Brand colors |
| `--ls-on-primary` | White or near-black, whichever reads better on the primary color (WCAG AA) |
| `--ls-radius` | Corner Radius |
| `--ls-font`, `--ls-heading-font` | Font and Heading Font |

Also available inside `.ls-root`: `--ls-text`, `--ls-muted`, `--ls-border`, `--ls-surface`.

CSS order on the page: brand variables → `layouts/base.css` → layout CSS → Settings **Custom CSS**.

## Minimal example

```jinja
<div class="ls-root my-login" dir="{{ ls.dir }}" lang="{{ ls.lang }}">
  <header class="my-login__brand">
    {{ ls_logo() }}
    <h1>{{ ls.brand.name }}</h1>
  </header>
  <section class="my-login__form">{{ login_form }}</section>
  <footer>{{ ls_versions() }}{{ ls_powered_by() }}</footer>
</div>
```

```css
.my-login {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	gap: 2rem;
	padding: 2rem 1rem;
	background: linear-gradient(135deg, var(--ls-primary), var(--ls-secondary));
}
.my-login__brand { color: var(--ls-on-primary); text-align: center; }
.my-login__form {
	width: 100%;
	max-width: 420px;
	padding: 2rem;
	border-radius: var(--ls-radius);
	background: var(--ls-surface);
}
```

Tips:

- Start the root element with `class="ls-root"`; `base.css` uses it to make the page full screen and to restyle the stock form.
- Wrap `{{ login_form }}` in a block element or a **column** flex container. In a row flex container the form shrinks to its content width.
- Use logical properties (`margin-inline`, `inset-inline-start`) so the layout also works right-to-left.
