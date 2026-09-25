# APiHole

A small Python client for the **Pi-hole v6** REST API.

> **Still on Pi-hole v5?** Version 1.0 and later only work with Pi-hole v6.
> Pin the old release with `pip install 'APiHole==0.0.3'`. Its source stays
> on the [`v5-legacy`](https://github.com/sdebby/APiHole/tree/v5-legacy) branch.
> It is frozen, since Pi-hole v5 is end-of-life.

## Install

```bash
pip install APiHole
```

Requires Python 3.9+.

## Authentication: use an app password

Pi-hole v6 authenticates with sessions. APiHole logs in with a password, sends
the session id with every request, and logs out when you are done.

Don't give scripts your admin password. Create an **app password** instead:

1. In the Pi-hole web interface, open **Settings → Web interface / API**.
2. Click **Configure app password**, copy the generated password, and click
   **Enable new app password**.

An app password also skips two-factor authentication. If your Pi-hole has no
password at all, pass `password=None` and APiHole does not log in.

> Pi-hole allows only a limited number of API sessions at once. **Always use
> `with`** (or call `close()`) so the session is released. Scripts that leak
> sessions eventually get `RateLimitError` (HTTP 429) until the old sessions
> expire.

## Usage

```python
from APiHole import PiHole

with PiHole("pi.hole", "your-app-password") as ph:
    print(ph.version()["ftl"]["local"]["version"])
    print(ph.summary()["queries"]["blocked"])

    ph.disable(30)          # pause blocking for 30 seconds
    ph.enable()

    ph.deny("ads.example.com", comment="added from script")
    ph.remove_deny("ads.example.com")
```

Connection options:

```python
PiHole(
    host="192.168.1.2:8080",   # hostname or IP, optional port
    password="...",            # None if the Pi-hole has no password
    https=True,                # default False
    verify=False,              # TLS verification, or a path to a CA bundle
    timeout=10,                # seconds per request
    totp=None,                 # 2FA code, only if not using an app password
)
```

### Methods

| Method | Returns |
|---|---|
| `version()` | dict of core/web/FTL/docker versions |
| `summary()` | dict with `queries`, `clients`, `gravity` counters |
| `gravity_last_update()` | `datetime` (UTC) or `None` |
| `blocking_status()` | `{"blocking": "enabled" \| "disabled" \| …, "timer": …}` |
| `enable()` / `disable(seconds=None)` | new blocking status; `None` or `0` means indefinitely |
| `top_domains(count=10, blocked=False)` | list of `{"domain", "count"}` |
| `top_clients(count=10, blocked=False)` | list of `{"ip", "name", "count"}` |
| `recent_blocked(count=1)` | list of domain names |
| `upstreams()` | list of upstream servers with counts |
| `query_types()` | dict of record type → count |
| `cache_info()` | DNS cache metrics |
| `clients()` | network devices |
| `history()` | 10-minute buckets of total/blocked/cached/forwarded |
| `history_clients()` | per-client 10-minute buckets |
| `dns_port()` | int |
| `allow(domain, comment=None)` / `remove_allow(domain)` | allow list, exact |
| `allow_regex(pattern, comment=None)` / `remove_allow_regex(pattern)` | allow list, regex |
| `deny(domain, comment=None)` / `remove_deny(domain)` | deny list, exact |
| `deny_regex(pattern, comment=None)` / `remove_deny_regex(pattern)` | deny list, regex |
| `update_gravity(timeout=600)` | gravity log output (`pihole -g`) |
| `restart_dns()` | `None` |

For anything else, `request(method, path, **kwargs)` calls any endpoint under
`/api` with the same session handling and returns the `requests.Response`.
Your Pi-hole documents every endpoint at `http://pi.hole/api/docs`.

### Errors

Every error is a subclass of `PiHoleError`:

| Exception | When |
|---|---|
| `PiHoleConnectionError` | the host could not be reached or timed out |
| `AuthenticationError` | 401: wrong password or missing 2FA code |
| `NotFoundError` | 404: e.g. removing a domain that is not on the list |
| `RateLimitError` | 429: too many requests or no free API sessions |
| `APIError` | any other HTTP error; has `status_code`, `key`, `message`, `hint` |

If a session expires in the middle of a script, APiHole logs in again once and
retries the request.

APiHole logs to the `APiHole` logger and never configures logging itself.

## Migrating from 0.0.3

1.0 is a clean break. Create a client once, not a static call per request.
Whitelist/blacklist are now called allow/deny, as in Pi-hole itself.

| 0.0.3 | 1.0 |
|---|---|
| `PiHole.GetVer(IP)` | `ph.version()` |
| `PiHole.GetSummary(IP, API, Raw_data)` | `ph.summary()` (always raw numbers) |
| `PiHole.GetStatus(IP, API)` | `ph.blocking_status()` |
| `PiHole.GetGravity(IP, API)` | `ph.gravity_last_update()` |
| `PiHole.Enable(IP, API)` | `ph.enable()` |
| `PiHole.Disable(IP, API, Time)` | `ph.disable(seconds)` |
| `PiHole.GetTopItems(IP, API, n)` | `ph.top_domains(n)` and `ph.top_domains(n, blocked=True)` |
| `PiHole.GetTopClients(IP, API, n)` | `ph.top_clients(n)` |
| `PiHole.GetTopClientsBlocked(IP, API, n)` | `ph.top_clients(n, blocked=True)` |
| `PiHole.GetRecentBlocked(IP, API)` | `ph.recent_blocked()` |
| `PiHole.GetDestination(IP, API)` | `ph.upstreams()` |
| `PiHole.GetQueryTypes(IP, API)` | `ph.query_types()` |
| `PiHole.GetCacheInfo(IP, API)` | `ph.cache_info()` |
| `PiHole.GetClientNames(IP, API)` | `ph.clients()` |
| `PiHole.GetOverTimeData10mins(IP, API)` | `ph.history()` |
| `PiHole.GetOverTimeDataClients(IP, API)` | `ph.history_clients()` |
| `PiHole.GetDnsPort(IP, API)` | `ph.dns_port()` |
| `PiHole.AddWhite(IP, API, d)` | `ph.allow(d)` |
| `PiHole.AddBlock(IP, API, d)` | `ph.deny(d)` |
| `PiHole.RemoveBlock(IP, API, d)` | `ph.remove_deny(d)` |
| `PiHole.AddRegexBlock(IP, API, r)` | `ph.deny_regex(r)` |
| `PiHole.RemoveRegexBlock(IP, API, r)` | `ph.remove_deny_regex(r)` |

Other changes:

- Failures raise exceptions instead of returning `None` or `True`.
- The API token from `setupVars.conf` no longer exists. Use an app password.
- Response shapes follow the v6 API, so dict keys differ from v5.

## Development

```bash
python -m venv .venv
.venv/bin/pip install -e ".[test]"
.venv/bin/pytest
```

`example.py` is a smoke test against a real Pi-hole:
`PIHOLE_HOST=pi.hole PIHOLE_PASSWORD=... python example.py`.

## Feedback

Open an issue on [GitHub](https://github.com/sdebby/APiHole/issues) or email
shmulik.debby@gmail.com.
