"""No network: regressions for session isolation and owned report writes."""
from types import SimpleNamespace
import pytest
import jwt
from services import db, auth


def token():
    return jwt.encode({"sub": "00000000-0000-0000-0000-000000000001"}, "test-only-key-not-a-production-secret", algorithm="HS256")


def test_environment_config_without_secrets(monkeypatch):
    class MissingSecrets:
        def get(self, name):
            raise FileNotFoundError("No secrets")
    monkeypatch.setattr(db.st, "secrets", MissingSecrets())
    monkeypatch.setenv("SUPABASE_URL", "https://example.invalid")
    monkeypatch.setenv("SUPABASE_KEY", "test-public-key")
    assert db.get_supabase_config() == ("https://example.invalid", "test-public-key")


def test_logout_clears_uploaded_data_tokens_and_admin_caches(monkeypatch):
    state = {"user": {}, "access_token": "private", "cached_users": [], "erp_data": {}, "report_pdf": b"report"}
    monkeypatch.setattr(auth.st, "session_state", state)
    monkeypatch.setattr(auth, "get_supabase", lambda: SimpleNamespace(auth=SimpleNamespace(sign_out=lambda: None)))
    auth.logout()
    assert state == {}


@pytest.mark.parametrize("save", [db.save_risk_analysis, db.save_credit_report, db.save_audit_report])
def test_no_anonymous_financial_writes(monkeypatch, save):
    def forbidden(*args, **kwargs):
        raise AssertionError("No database call expected")
    monkeypatch.setattr(db, "get_supabase", forbidden)
    monkeypatch.setattr(db, "get_auth_supabase", forbidden)
    assert save({"company_name": "Test"}) is False


def test_failed_credit_insert_never_strips_owner(monkeypatch):
    rows = []
    class Table:
        def insert(self, row):
            rows.append(dict(row))
            return self
        def execute(self):
            raise RuntimeError("Permission denied")
    monkeypatch.setattr(db, "get_auth_supabase", lambda _: SimpleNamespace(table=lambda _: Table()))
    monkeypatch.setattr(db.st, "warning", lambda _: None)
    assert db.save_credit_report({"company_name": "Test", "raw_data": {"evidence": 1}}, token()) is False
    assert len(rows) == 1
    assert rows[0]["user_id"].endswith("1")
    assert rows[0]["raw_data"]["evidence"] == 1


def test_profile_fallback_does_not_overwrite_existing_role(monkeypatch):
    calls = []
    class Table:
        def upsert(self, row, **kwargs):
            calls.append((row, kwargs))
            return self
        def execute(self):
            return None
    monkeypatch.setattr(auth, "get_auth_supabase", lambda _: SimpleNamespace(table=lambda _: Table()))
    auth.ensure_user_profile("u", "test@example.invalid", "Name", "token")
    assert calls[0][1] == {"on_conflict": "id", "ignore_duplicates": True}


def test_history_requires_authentication_and_known_table(monkeypatch):
    monkeypatch.setattr(db, "get_auth_supabase", lambda _: pytest.fail("Must not call DB"))
    assert db.get_recent_analyses("credit_reports") == []
    assert db.get_recent_analyses("user_profiles", access_token="token") == []


def test_legacy_api_cannot_charge_or_return_unvalidated_score():
    import asyncio
    from fastapi import HTTPException
    from main import analyze, ScoringRequest
    with pytest.raises(HTTPException) as error:
        asyncio.run(analyze(ScoringRequest(company_name="Test", revenue=1, ebitda=-2, total_debt=0)))
    assert error.value.status_code == 503
