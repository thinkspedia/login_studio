### Login Studio Plugin Example

A minimal Frappe app that extends [Login Studio](../../README.md) without touching its code. It uses every plugin hook:

| Hook | What this example does |
|---|---|
| `login_studio_layouts` | Ships the **Aurora** layout (`login_layouts/lspe_aurora/`) |
| `login_studio_context` | Adds `ls.extra.support_email` |
| `login_studio_slots` | Puts a "Need help signing in?" line in the `below_form` slot of every layout |
| `login_studio_assets` | Adds a small stylesheet for that line |

All of it is in `hooks.py` and `login.py`. Copy this folder as a starting point for your own plugin, rename the app, and prefix your layout names (here `lspe_`) so they never clash with other apps.

Install (Login Studio must be installed first):

```bash
bench get-app <your-plugin-repo>
bench --site your-site install-app login_studio_plugin_example
```

The plugin guide is in [docs/plugins.md](../../docs/plugins.md).

License: MIT
