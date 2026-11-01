# Security policy

## Supported versions

| Version | Frappe | Supported |
|---|---|---|
| 0.1.x | v15, v16 | Yes |

## Reporting a vulnerability

Please do **not** open a public issue for security problems.

Report them privately through GitHub: **Security → Report a vulnerability** on this repository ([direct link](https://github.com/thinkspedia/login_studio/security/advisories/new)). Include the Login Studio and Frappe versions, the steps to reproduce, and the impact you expect.

We will acknowledge the report and agree on a fix and disclosure timeline with you.

## Scope notes

- Login Studio renders on a page that anyone can open. Layout templates run in Frappe's Jinja sandbox, can only be edited by System Managers, and cannot contain JavaScript; JavaScript can only come from installed apps through the `login_studio_assets` hook.
- Showing app versions on the login page is off by default because exact versions help attackers; keep it off on production sites.
