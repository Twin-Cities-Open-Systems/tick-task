"""Tests for LAN token access control.

These exist because lan_mode/lan_token were declared in config and enforced
nowhere -- config fields that looked like an access control while every
endpoint stayed open. The tests pin the behavior so that cannot regress
silently.
"""

import pytest

from tick_task.config import settings


@pytest.fixture
def lan_off(monkeypatch):
    monkeypatch.setattr(settings, "lan_mode", False)
    monkeypatch.setattr(settings, "lan_token", None)


@pytest.fixture
def lan_on_no_token(monkeypatch):
    monkeypatch.setattr(settings, "lan_mode", True)
    monkeypatch.setattr(settings, "lan_token", None)


@pytest.fixture
def lan_on(monkeypatch):
    monkeypatch.setattr(settings, "lan_mode", True)
    monkeypatch.setattr(settings, "lan_token", "correct-horse-battery-staple")


def test_lan_mode_off_leaves_api_open(client, lan_off):
    """Default posture is unchanged: loopback-only, no token required."""
    assert client.get("/api/v1/health").status_code == 200


def test_lan_mode_on_without_token_fails_closed(client, lan_on_no_token):
    """A half-configured deployment must refuse, never fall open."""
    r = client.get("/api/v1/health")
    assert r.status_code == 503
    assert "lan_token" in r.json()["detail"]


def test_lan_mode_on_rejects_missing_token(client, lan_on):
    r = client.get("/api/v1/health")
    assert r.status_code == 401
    assert r.headers.get("WWW-Authenticate") == "Bearer"


def test_lan_mode_on_rejects_wrong_token(client, lan_on):
    r = client.get("/api/v1/health", headers={"Authorization": "Bearer nope"})
    assert r.status_code == 401


def test_lan_mode_on_rejects_bare_token_without_scheme(client, lan_on):
    """The scheme is part of the expected value, not optional."""
    r = client.get(
        "/api/v1/health",
        headers={"Authorization": "correct-horse-battery-staple"},
    )
    assert r.status_code == 401


def test_lan_mode_on_accepts_correct_token(client, lan_on):
    r = client.get(
        "/api/v1/health",
        headers={"Authorization": "Bearer correct-horse-battery-staple"},
    )
    assert r.status_code == 200


def test_write_endpoints_are_protected_too(client, lan_on):
    """Not just reads -- POST/PUT/DELETE were equally open before this."""
    r = client.post("/api/v1/tasks", json={"title": "x"})
    assert r.status_code == 401
