# Contributing to Login Studio

Thanks for helping. New layouts, translations, plugins, bug reports and fixes are all welcome.

## Before you start

- For anything larger than a small fix, open an issue first so we can agree on the approach.
- Security problems: see [SECURITY.md](SECURITY.md), not a public issue.

## Development setup

```bash
cd frappe-bench
bench get-app https://github.com/thinkspedia/login_studio --branch develop
bench --site dev.localhost install-app login_studio
cd apps/login_studio
pre-commit install
```

Run the tests:

```bash
bench --site dev.localhost set-config allow_tests true
bench --site dev.localhost run-tests --app login_studio
```

## Rules for changes

- Target the `develop` branch. `version-15` and `version-16` are release branches.
- The code must work on **Frappe v15 and v16** and stay **Python 3.10 compatible**. Put anything version-specific in `login_studio/compat.py`. CI runs every test on both versions; a pull request is merged only when both pass.
- Never copy Frappe's login form. Layouts wrap it via `{{ login_form }}`, so upstream fixes keep flowing in.
- Escape anything that is not trusted HTML. Frappe's Jinja does not auto-escape.
- Add or update tests with the change, and keep pull requests small and focused on one thing.
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:` …).

## Adding a layout

Create `login_studio/layouts/<name>/` with `layout.json`, `template.html` and `style.css`, following the [layout contract](docs/layout-contract.md). Make it mobile-first and check it at 320, 768 and 1440 px. It is picked up on `bench migrate`.

## Adding a translation

Add `login_studio/translations/<language>.csv` with `source,translation,context` rows. Only translate strings Frappe does not already translate, so terms stay the same as in Desk.

## License

By contributing you agree that your contributions are licensed under the [MIT License](LICENSE).
