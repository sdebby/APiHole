"""Smoke test against a live Pi-hole v6.

    PIHOLE_HOST=pi.hole PIHOLE_PASSWORD=<app password> python example.py

It reads stats, disables blocking for 5 seconds and re-enables it, then adds
and removes a test domain on the deny list. Nothing is left behind.
"""
import os

from APiHole import PiHole, PiHoleError

HOST = os.environ.get("PIHOLE_HOST", "pi.hole")
PASSWORD = os.environ.get("PIHOLE_PASSWORD")  # None if the Pi-hole has no password
TEST_DOMAIN = "apihole-smoke-test.example"

try:
    with PiHole(HOST, PASSWORD) as ph:
        version = ph.version()
        print("FTL version:", version["ftl"]["local"]["version"])

        summary = ph.summary()
        print("Queries today:", summary["queries"]["total"])
        print("Blocked today:", summary["queries"]["blocked"])
        print("Gravity updated:", ph.gravity_last_update())
        print("Blocking:", ph.blocking_status()["blocking"])

        print("Top domains:")
        for item in ph.top_domains(5):
            print(f"  {item['domain']}: {item['count']}")
        print("Top blocked:")
        for item in ph.top_domains(5, blocked=True):
            print(f"  {item['domain']}: {item['count']}")
        print("Top clients:")
        for item in ph.top_clients(5):
            print(f"  {item['name'] or item['ip']}: {item['count']}")

        print("Recently blocked:", ph.recent_blocked(3))
        print("Upstreams:", [u["ip"] for u in ph.upstreams()])
        print("Query types:", ph.query_types())
        print("DNS port:", ph.dns_port())

        print("Disable 5s:", ph.disable(5))
        print("Enable:", ph.enable())

        ph.deny(TEST_DOMAIN, comment="APiHole smoke test")
        print("Added", TEST_DOMAIN, "to the deny list")
        ph.remove_deny(TEST_DOMAIN)
        print("Removed", TEST_DOMAIN, "from the deny list")
    # Leaving the with-block logged out and freed the API session.
except PiHoleError as exc:
    raise SystemExit(f"Pi-hole error: {exc}")
