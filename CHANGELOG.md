# Changelog

## 1.0.0 (unreleased)

A rewrite for the Pi-hole v6 REST API. It does not work with Pi-hole v5; for
v5, use `APiHole==0.0.3`.

### Changed
- `PiHole` is now a client instance with a session:
  `with PiHole(host, password) as ph: ...`. It logs in once, sends the session
  as `X-FTL-SID`, logs in again once after a 401, and always logs out on exit.
- Authentication uses the web password or an app password, not the v5 API token.
- Methods use snake_case and v6 terms (allow/deny). See the migration table in
  the README.
- Errors raise `PiHoleError` subclasses instead of returning `None` or `True`.
- Responses are the v6 JSON payloads.
- Importing the package no longer calls `logging.basicConfig`.

### Added
- `https`, `verify`, `timeout` and `totp` options.
- `remove_allow`, `allow_regex`, `remove_allow_regex`, `update_gravity`,
  `restart_dns`, and a generic `request()` for any other endpoint.
- Regex and domain path segments are URL-escaped.
- Type hints (`py.typed`), tests and CI.

### Removed
- `setup.py`, replaced by `pyproject.toml`.

## 0.0.3 (2024-06)

Last release for Pi-hole v5 (`/admin/api.php`). Tagged `v0.0.3`; source on the
`v5-legacy` branch.
