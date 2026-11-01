# Plugin guide

Any Frappe app can extend Login Studio from its own `hooks.py`, without changing Login Studio's code. A complete working example is in [`examples/login_studio_plugin_example`](../examples/login_studio_plugin_example); copy it as a starting point.

Add `required_apps = ["login_studio"]` to your `hooks.py` so your app is never installed without it.

## Hooks

### `login_studio_layouts`: ship layouts

```python
login_studio_layouts = ["login_layouts"]
```

Each entry is a folder **inside your app's Python package**; every sub-folder with a `layout.json` is one layout, in the same format as Login Studio's own (see the [layout contract](layout-contract.md)):

```
my_app/login_layouts/my_app_harbor/
├── layout.json      {"title": "Harbor", "description": "..."}
├── template.html
└── style.css
```

- Layouts are synced when your app is installed and on every `bench migrate`, and removed when your app is uninstalled. If one of them was the active layout, the site falls back to Split Hero.
- They show up as **Plugin** layouts: read-only in Desk, but users can duplicate them.
- **Prefix layout names with your app name.** A name that is already taken by another app or a user's custom layout is skipped, with an Error Log entry.
- Folders outside your app package are refused.

### `login_studio_context`: add data

```python
login_studio_context = ["my_app.login.add_context"]
```

```python
from login_studio.api import escape

def add_context(ls):
	ls["extra"]["support_email"] = escape("support@example.com")
```

The function receives the `ls` dict before the layout renders and changes it in place. Put your own values under `ls["extra"]`; you may also adjust existing values. **Templates print `ls` values as they are**, so escape anything that is not trusted HTML (`login_studio.api.escape`).

### `login_studio_slots`: inject HTML

```python
login_studio_slots = {
	"below_form": "my_app.login.help_notice",
}
```

```python
import frappe
from login_studio.api import Markup

def help_notice(ls):
	email = ls["extra"].get("support_email")
	if not email:
		return ""
	link = Markup('<a href="mailto:{0}">{0}</a>').format(email)
	return Markup('<p class="my-help">{} {}</p>').format(frappe._("Need help signing in?"), link)
```

Slot functions receive `ls` (after all context hooks) and return HTML, or an empty string to render nothing. The HTML is inserted as-is, so build it with `Markup(...).format(...)`, which escapes the arguments.

Every built-in layout offers these slots:

| Slot | Where |
|---|---|
| `hero` | Next to the brand name / headline |
| `above_form` | Directly above the sign-in form |
| `below_form` | Directly below the sign-in form |
| `footer` | In the footer, before "Powered by" |

Custom layouts place slots with `{{ ls_slot("below_form") }}`. Unknown slot names are ignored.

### `login_studio_assets`: add CSS / JavaScript

```python
login_studio_assets = {
	"css": ["/assets/my_app/css/login.css"],
	"js": ["/assets/my_app/js/login.js"],
}
```

Files are added to the login page (CSS in the head, JS deferred at the end). Only same-site paths (`/assets/...`) and `https://` URLs are accepted. This is the only way to add JavaScript to the login page: layouts and settings cannot store scripts.

## Failure handling

A hook that raises is skipped: the page still renders without it, and the error is written to Error Log (at most once every 5 minutes per hook). A broken layout falls back to the stock Frappe login.

## Public Python API

`login_studio.api` is stable: it only changes incompatibly in a new major version. Everything else in the package is internal.

| Name | Purpose |
|---|---|
| `API_VERSION` | Integer, currently `1` |
| `SLOT_NAMES` | `("hero", "above_form", "below_form", "footer")` |
| `escape`, `Markup` | Re-exported from markupsafe, for building safe HTML |
| `get_layout_context()` | The `ls` dict built from the saved settings, plugin hooks applied |
| `render_layout(name)` | `{"before", "after", "css", "assets"}` for any layout, enabled or not |
