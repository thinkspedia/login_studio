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

## Releasing

For maintainers:

1. Open a `chore: Release vX.Y.Z` PR into `develop` that bumps `__version__` in `login_studio/__init__.py`, dates the CHANGELOG entry and updates the README badge. Merge it once CI passes.
2. Fast-forward `version-15` and `version-16` to `develop`.
3. Publish the GitHub release `vX.Y.Z` on that commit.

Publishing the release runs `.github/workflows/publish-marketplace.yml`, which opens a PR advertising the release on the [Frappe Marketplace](https://github.com/frappe/marketplace) from the `tomysmile/marketplace` fork, using the `MARKETPLACE_PR_TOKEN` secret (a classic token with `public_repo`). The marketplace check installs the release on a Pilot bench and merges the PR when it passes. To re-publish, run the workflow by hand from the Actions tab.

## License

By contributing you agree that your contributions are licensed under the [MIT License](LICENSE).
