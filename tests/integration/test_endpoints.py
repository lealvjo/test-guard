import uuid

import pytest

from main import app


def _uid(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def _create_automation_payload(name):
    return {
        "name": name,
        "squad": "QA",
        "type": "Backend",
        "description": "Automation created by integration test",
        "language": "Python",
        "cucumber": "BDD",
        "launch_date": "2026-01-01",
        "git": f"https://example.com/{name}.git",
    }


@pytest.mark.integration
def test_automation_crud_flow(client):
    name = _uid("it-automation")
    payload = _create_automation_payload(name)

    create_resp = client.post("/register-automation", json=payload)
    assert create_resp.status_code == 201
    automation_id = create_resp.get_json()["automation_id"]

    get_resp = client.get(f"/automations/{automation_id}")
    assert get_resp.status_code == 200
    assert get_resp.get_json()["automation"]["name"] == name

    search_resp = client.get(f"/automations/paginated?page=1&per_page=10&search={name}")
    assert search_resp.status_code == 200
    search_data = search_resp.get_json()
    assert search_data["total_automations"] >= 1
    assert any(item["name"] == name for item in search_data["automations"])

    delete_resp = client.delete(f"/automations/{automation_id}")
    assert delete_resp.status_code == 200

    get_after_delete_resp = client.get(f"/automations/{automation_id}")
    assert get_after_delete_resp.status_code == 404


@pytest.mark.integration
def test_contract_endpoints_flow(client):
    collection_name = _uid("it-contract")
    contract_name = "UserContract"

    check_name_resp = client.post("/contracts/check-name", json={"name": collection_name})
    assert check_name_resp.status_code == 200
    assert check_name_resp.get_json()["available"] is True

    payload = {
        "name": collection_name,
        "squad": "QA",
        "repository_url": f"https://example.com/{collection_name}.git",
        "schemas": [
            {
                "contract": contract_name,
                "expected": {
                    "type": "object",
                    "properties": {"id": {"type": "integer"}},
                    "required": ["id"],
                },
            }
        ],
    }
    create_resp = client.post("/contract", json=payload)
    assert create_resp.status_code == 201

    search_resp = client.get(f"/contracts/search?name={collection_name}&contract={contract_name}")
    assert search_resp.status_code == 200
    assert search_resp.get_json()["total"] >= 1

    invalid_validate_resp = client.post(
        "/contract-validate",
        json={
            "collection_name": collection_name,
            "contract_name": contract_name,
            "body_to_validate": {"id": "invalid-type"},
        },
    )
    assert invalid_validate_resp.status_code in (200, 400)


@pytest.mark.integration
def test_report_endpoints_flow(client):
    automation_name = _uid("it-report-automation")
    create_automation_resp = client.post("/register-automation", json=_create_automation_payload(automation_name))
    assert create_automation_resp.status_code == 201
    automation_id = create_automation_resp.get_json()["automation_id"]

    report_resp = client.post(
        "/report",
        json={
            "automation_id": automation_id,
            "status": "PASSED",
            "url_report": "https://example.com/report",
            "tests": 10,
            "junit": {
                "testsuite": {"name": "suite-api", "tests": 10, "failures": 0}
            },
        },
    )
    assert report_resp.status_code == 201

    reports_paginated_resp = client.get(f"/reports/paginated?page=1&per_page=20&search={automation_name}")
    assert reports_paginated_resp.status_code == 200
    data = reports_paginated_resp.get_json()
    assert data["total_reports"] >= 1
    assert isinstance(data["reports"][0]["junit"], dict)


@pytest.mark.integration
def test_report_accepts_null_junit(client):
    automation_name = _uid("it-report-null-junit")
    create_automation_resp = client.post("/register-automation", json=_create_automation_payload(automation_name))
    assert create_automation_resp.status_code == 201
    automation_id = create_automation_resp.get_json()["automation_id"]

    report_resp = client.post(
        "/report",
        json={
            "automation_id": automation_id,
            "status": "PASSED",
            "url_report": "https://example.com/report-null-junit",
            "tests": 3,
            "junit": None,
        },
    )
    assert report_resp.status_code == 201


@pytest.mark.integration
def test_open_junit_report_page(client):
    automation_name = _uid("it-junit-page")
    create_automation_resp = client.post("/register-automation", json=_create_automation_payload(automation_name))
    assert create_automation_resp.status_code == 201
    automation_id = create_automation_resp.get_json()["automation_id"]

    create_report_resp = client.post(
        "/report",
        json={
            "automation_id": automation_id,
            "status": "PASSED",
            "url_report": "https://example.com/report-junit-page",
            "tests": 2,
            "junit": {
                "testsuite": {
                    "name": "suite-smoke",
                    "tests": 2,
                    "failures": 0,
                    "testcase": [
                        {"classname": "smoke.test_api", "name": "test_health", "time": "0.01"},
                        {"classname": "smoke.test_api", "name": "test_ping", "time": "0.02"},
                    ],
                }
            },
        },
    )
    assert create_report_resp.status_code == 201

    reports_resp = client.get(f"/reports/paginated?page=1&per_page=10&search={automation_name}")
    assert reports_resp.status_code == 200
    report_id = reports_resp.get_json()["reports"][0]["id_report"]

    junit_page_resp = client.get(f"/reports/{report_id}/junit")
    assert junit_page_resp.status_code == 200
    assert b"Relat" in junit_page_resp.data
