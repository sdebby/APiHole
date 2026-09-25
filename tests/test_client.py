import json
from datetime import datetime, timezone

import pytest
import requests
import responses
from responses import matchers

from APiHole import (
    APIError,
    AuthenticationError,
    NotFoundError,
    PiHole,
    PiHoleConnectionError,
    RateLimitError,
)

BASE = "http://pi.hole/api"


def auth_ok(sid="sid-1"):
    return responses.Response(
        responses.POST,
        f"{BASE}/auth",
        json={"session": {"valid": True, "totp": False, "sid": sid, "validity": 1800}},
    )


def sent_json(call):
    return json.loads(call.request.body)


@pytest.fixture
def rsps():
    with responses.RequestsMock() as r:
        yield r


# -- authentication ----------------------------------------------------------


def test_login_stores_sid_and_sends_header(rsps):
    rsps.add(auth_ok("abc"))
    rsps.get(f"{BASE}/stats/summary", json={"queries": {}, "took": 0.1})
    rsps.delete(f"{BASE}/auth", status=204)

    with PiHole("pi.hole", "secret") as ph:
        assert ph.authenticated
        assert ph.summary() == {"queries": {}}

    login, summary, logout = rsps.calls
    assert sent_json(login) == {"password": "secret"}
    assert "X-FTL-SID" not in login.request.headers
    assert summary.request.headers["X-FTL-SID"] == "abc"
    assert logout.request.headers["X-FTL-SID"] == "abc"
    assert not ph.authenticated


def test_totp_is_sent_as_int(rsps):
    rsps.add(auth_ok())
    rsps.delete(f"{BASE}/auth", status=204)
    with PiHole("pi.hole", "secret", totp="123456"):
        pass
    assert sent_json(rsps.calls[0]) == {"password": "secret", "totp": 123456}


def test_lazy_login_without_context_manager(rsps):
    rsps.add(auth_ok())
    rsps.get(f"{BASE}/dns/blocking", json={"blocking": "enabled", "timer": None})
    ph = PiHole("pi.hole", "secret")
    assert ph.blocking_status() == {"blocking": "enabled", "timer": None}
    assert [c.request.method for c in rsps.calls] == ["POST", "GET"]


def test_no_password_means_no_auth_calls(rsps):
    rsps.get(f"{BASE}/dns/blocking", json={"blocking": "enabled", "timer": None})
    with PiHole("pi.hole") as ph:
        ph.blocking_status()
    assert len(rsps.calls) == 1
    assert "X-FTL-SID" not in rsps.calls[0].request.headers


def test_wrong_password_raises_authentication_error(rsps):
    rsps.post(
        f"{BASE}/auth",
        status=401,
        json={"error": {"key": "unauthorized", "message": "Unauthorized", "hint": None}},
    )
    with pytest.raises(AuthenticationError) as exc:
        with PiHole("pi.hole", "wrong"):
            pass
    assert exc.value.status_code == 401
    assert exc.value.key == "unauthorized"
    assert len(rsps.calls) == 1  # no logout: there is no session to free


def test_invalid_session_in_200_raises(rsps):
    rsps.post(
        f"{BASE}/auth",
        json={"session": {"valid": False, "sid": None, "message": "password incorrect"}},
    )
    with pytest.raises(AuthenticationError, match="password incorrect"):
        PiHole("pi.hole", "wrong").login()


def test_401_relogs_in_once_and_retries(rsps):
    rsps.add(auth_ok("old"))
    rsps.get(f"{BASE}/stats/summary", status=401, json={"error": {"key": "unauthorized"}})
    rsps.add(auth_ok("new"))
    rsps.get(f"{BASE}/stats/summary", json={"queries": {"total": 5}})

    ph = PiHole("pi.hole", "secret")
    assert ph.summary() == {"queries": {"total": 5}}
    methods = [c.request.method for c in rsps.calls]
    assert methods == ["POST", "GET", "POST", "GET"]
    assert rsps.calls[3].request.headers["X-FTL-SID"] == "new"


def test_second_401_is_raised_not_retried_forever(rsps):
    rsps.add(auth_ok("a"))
    rsps.get(f"{BASE}/stats/summary", status=401)
    rsps.add(auth_ok("b"))
    rsps.get(f"{BASE}/stats/summary", status=401)
    with pytest.raises(AuthenticationError):
        PiHole("pi.hole", "secret").summary()
    assert len(rsps.calls) == 4


def test_exit_logs_out_even_when_body_raises(rsps):
    rsps.add(auth_ok())
    rsps.delete(f"{BASE}/auth", status=204)
    with pytest.raises(RuntimeError):
        with PiHole("pi.hole", "secret"):
            raise RuntimeError("boom")
    assert rsps.calls[-1].request.method == "DELETE"
    assert rsps.calls[-1].request.url == f"{BASE}/auth"


def test_failed_logout_does_not_mask_original_error(rsps):
    rsps.add(auth_ok())
    rsps.delete(f"{BASE}/auth", status=500)
    with pytest.raises(RuntimeError):
        with PiHole("pi.hole", "secret"):
            raise RuntimeError("boom")


def test_logout_tolerates_expired_session(rsps):
    rsps.add(auth_ok())
    rsps.delete(f"{BASE}/auth", status=401)
    ph = PiHole("pi.hole", "secret")
    ph.login()
    ph.logout()
    assert not ph.authenticated


# -- errors ------------------------------------------------------------------


def test_429_raises_rate_limit_error(rsps):
    rsps.add(auth_ok())
    rsps.get(
        f"{BASE}/stats/summary",
        status=429,
        json={
            "error": {
                "key": "api_seats_exceeded",
                "message": "API seats exceeded",
                "hint": "increase webserver.api.max_sessions",
            }
        },
    )
    with pytest.raises(RateLimitError) as exc:
        PiHole("pi.hole", "secret").summary()
    assert exc.value.key == "api_seats_exceeded"
    assert "max_sessions" in str(exc.value)


def test_404_raises_not_found(rsps):
    rsps.delete(f"{BASE}/domains/deny/exact/nope.example", status=404)
    with pytest.raises(NotFoundError):
        PiHole().remove_deny("nope.example")


def test_other_http_error_raises_api_error_without_json_body(rsps):
    rsps.get(f"{BASE}/stats/summary", status=500, body="oops")
    with pytest.raises(APIError) as exc:
        PiHole().summary()
    assert exc.value.status_code == 500


def test_network_error_is_wrapped(rsps):
    rsps.get(f"{BASE}/stats/summary", body=requests.ConnectionError("refused"))
    with pytest.raises(PiHoleConnectionError):
        PiHole().summary()


# -- endpoints ---------------------------------------------------------------


def test_https_and_verify_options(rsps):
    rsps.get("https://10.0.0.2:8443/api/info/version", json={"version": {"ftl": {}}})
    ph = PiHole("10.0.0.2:8443", https=True, verify=False)
    assert ph.version() == {"ftl": {}}
    assert rsps.calls[0].request.url.startswith("https://10.0.0.2:8443/api/")


def test_disable_none_sends_null_timer(rsps):
    rsps.post(
        f"{BASE}/dns/blocking",
        json={"blocking": "disabled", "timer": None},
        match=[matchers.json_params_matcher({"blocking": False, "timer": None})],
    )
    assert PiHole().disable()["blocking"] == "disabled"


def test_disable_zero_means_indefinitely(rsps):
    rsps.post(
        f"{BASE}/dns/blocking",
        json={"blocking": "disabled", "timer": None},
        match=[matchers.json_params_matcher({"blocking": False, "timer": None})],
    )
    PiHole().disable(0)


def test_disable_with_timer_and_enable(rsps):
    rsps.post(
        f"{BASE}/dns/blocking",
        json={"blocking": "disabled", "timer": 30},
        match=[matchers.json_params_matcher({"blocking": False, "timer": 30})],
    )
    rsps.post(
        f"{BASE}/dns/blocking",
        json={"blocking": "enabled", "timer": None},
        match=[matchers.json_params_matcher({"blocking": True, "timer": None})],
    )
    ph = PiHole()
    assert ph.disable(30)["timer"] == 30
    assert ph.enable()["blocking"] == "enabled"


def test_regex_is_url_quoted(rsps):
    pattern = r"(\.|^)ads?[0-9]*\.example\.com$"
    rsps.delete(
        f"{BASE}/domains/deny/regex/%28%5C.%7C%5E%29ads%3F%5B0-9%5D%2A%5C.example%5C.com%24",
        status=204,
    )
    PiHole().remove_deny_regex(pattern)


def test_deny_posts_domain_and_comment(rsps):
    rsps.post(
        f"{BASE}/domains/deny/exact",
        status=201,
        json={"domains": [{"domain": "ads.example"}], "processed": {"success": [], "errors": []}},
        match=[matchers.json_params_matcher({"domain": "ads.example", "comment": "test"})],
    )
    result = PiHole().deny("ads.example", comment="test")
    assert result["domains"][0]["domain"] == "ads.example"


@pytest.mark.parametrize(
    "method, url",
    [
        ("allow", f"{BASE}/domains/allow/exact"),
        ("allow_regex", f"{BASE}/domains/allow/regex"),
        ("deny_regex", f"{BASE}/domains/deny/regex"),
    ],
)
def test_add_methods_hit_the_right_list(rsps, method, url):
    rsps.post(url, status=201, json={"domains": [], "processed": {}},
              match=[matchers.json_params_matcher({"domain": "x.example"})])
    getattr(PiHole(), method)("x.example")


@pytest.mark.parametrize(
    "method, url",
    [
        ("remove_allow", f"{BASE}/domains/allow/exact/x.example"),
        ("remove_allow_regex", f"{BASE}/domains/allow/regex/x.example"),
        ("remove_deny", f"{BASE}/domains/deny/exact/x.example"),
    ],
)
def test_remove_methods_hit_the_right_list(rsps, method, url):
    rsps.delete(url, status=204)
    assert getattr(PiHole(), method)("x.example") is None


def test_stats_unwrap_their_payload(rsps):
    rsps.get(
        f"{BASE}/stats/top_domains",
        json={"domains": [{"domain": "a", "count": 3}]},
        match=[matchers.query_param_matcher({"count": "7", "blocked": "true"})],
    )
    rsps.get(
        f"{BASE}/stats/top_clients",
        json={"clients": [{"ip": "10.0.0.5", "name": "pc", "count": 9}]},
        match=[matchers.query_param_matcher({"count": "5", "blocked": "false"})],
    )
    rsps.get(f"{BASE}/stats/recent_blocked", json={"blocked": ["ads.example"]},
             match=[matchers.query_param_matcher({"count": "1"})])
    rsps.get(f"{BASE}/stats/upstreams", json={"upstreams": [{"ip": "1.1.1.1"}]})
    rsps.get(f"{BASE}/stats/query_types", json={"types": {"A": 10}})
    rsps.get(f"{BASE}/info/metrics", json={"metrics": {"dns": {"cache": {"size": 10000}}}})
    rsps.get(f"{BASE}/network/devices", json={"devices": [{"hwaddr": "aa"}]})
    rsps.get(f"{BASE}/history", json={"history": [{"timestamp": 1, "total": 2}]})
    rsps.get(f"{BASE}/history/clients", json={"clients": {}, "history": [], "took": 0.1})
    rsps.get(f"{BASE}/config/dns/port", json={"config": {"dns": {"port": 53}}})

    ph = PiHole()
    assert ph.top_domains(7, blocked=True) == [{"domain": "a", "count": 3}]
    assert ph.top_clients(5)[0]["name"] == "pc"
    assert ph.recent_blocked() == ["ads.example"]
    assert ph.upstreams() == [{"ip": "1.1.1.1"}]
    assert ph.query_types() == {"A": 10}
    assert ph.cache_info() == {"size": 10000}
    assert ph.clients() == [{"hwaddr": "aa"}]
    assert ph.history() == [{"timestamp": 1, "total": 2}]
    assert ph.history_clients() == {"clients": {}, "history": []}
    assert ph.dns_port() == 53


def test_gravity_last_update(rsps):
    rsps.get(f"{BASE}/stats/summary", json={"gravity": {"last_update": 1700000000}})
    rsps.get(f"{BASE}/stats/summary", json={"gravity": {"last_update": 0}})
    ph = PiHole()
    assert ph.gravity_last_update() == datetime(2023, 11, 14, 22, 13, 20, tzinfo=timezone.utc)
    assert ph.gravity_last_update() is None


def test_actions(rsps):
    rsps.post(f"{BASE}/action/gravity", body="  [i] Done.\n")
    rsps.post(f"{BASE}/action/restartdns", json={"status": "success"})
    ph = PiHole()
    assert "Done" in ph.update_gravity()
    assert ph.restart_dns() is None
