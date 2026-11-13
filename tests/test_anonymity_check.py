"""Tests for the anonymity classification. No network: the judge answer is faked."""
import sys
from pathlib import Path

import pytest
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import anonymity_check  # noqa: E402
from anonymity_check import classify  # noqa: E402

MINE = {"198.51.100.23"}


class Judge:
    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data


def judge_says(monkeypatch, data=None, error=None):
    def get(url, proxies=None, timeout=None):
        assert url == anonymity_check.JUDGE and url.startswith("http://")  # plain HTTP, or the proxy cannot add headers
        if error:
            raise error
        return Judge(data)
    monkeypatch.setattr(anonymity_check.requests, "get", get)


def test_transparent_when_your_ip_shows(monkeypatch):
    judge_says(monkeypatch, {"origin": "203.0.113.10", "headers": {"X-Forwarded-For": "198.51.100.23"}})
    assert classify("http://203.0.113.10:8080", MINE)["level"] == "transparent"


def test_anonymous_when_only_proxy_headers_show(monkeypatch):
    judge_says(monkeypatch, {"origin": "203.0.113.10", "headers": {"via": "1.1 squid", "Host": "httpbin.org"}})
    r = classify("http://203.0.113.10:8080", MINE)
    assert r["level"] == "anonymous" and r["detail"] == "Via"


def test_elite_when_nothing_shows(monkeypatch):
    judge_says(monkeypatch, {"origin": "203.0.113.10", "headers": {"Host": "httpbin.org", "User-Agent": "python-requests"}})
    assert classify("http://203.0.113.10:8080", MINE) == {
        "proxy": "http://203.0.113.10:8080", "level": "elite", "detail": "-", "origin": "203.0.113.10"}


@pytest.mark.parametrize("error", [requests.exceptions.ConnectTimeout("slow"), requests.exceptions.ProxyError("refused")])
def test_dead_when_the_proxy_fails(monkeypatch, error):
    judge_says(monkeypatch, error=error)
    assert classify("http://203.0.113.10:8080", MINE)["level"] == "dead"
