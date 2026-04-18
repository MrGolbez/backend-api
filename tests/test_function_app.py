import json
from unittest.mock import Mock

import azure.functions as func
import pytest
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError

import function_app


def make_request(method="GET"):
    return func.HttpRequest(
        method=method,
        url="/api/GetResumeCounter",
        body=None,
    )


def response_json(response):
    return json.loads(response.get_body().decode("utf-8"))


def test_options_request_returns_cors_preflight_response():
    response = function_app.GetResumeCounter(make_request("OPTIONS"))

    assert response.status_code == 204
    assert response.headers["Access-Control-Allow-Origin"] == "*"
    assert response.headers["Access-Control-Allow-Methods"] == "GET, OPTIONS"


def test_missing_settings_returns_configuration_error(monkeypatch):
    monkeypatch.delenv("STORAGE_CONNECTION_STRING", raising=False)
    monkeypatch.delenv("TABLE_NAME", raising=False)

    response = function_app.GetResumeCounter(make_request())

    assert response.status_code == 500
    assert response_json(response) == {"error": "Server configuration error."}


def test_existing_counter_is_incremented(monkeypatch):
    table_client = Mock()
    table_client.create_table.side_effect = ResourceExistsError("exists")
    table_client.get_entity.return_value = {"Count": 7}

    table_client_class = Mock()
    table_client_class.from_connection_string.return_value = table_client

    monkeypatch.setenv("STORAGE_CONNECTION_STRING", "UseDevelopmentStorage=true")
    monkeypatch.setenv("TABLE_NAME", "Counter")
    monkeypatch.setattr(function_app, "TableClient", table_client_class)

    response = function_app.GetResumeCounter(make_request())

    assert response.status_code == 200
    assert response_json(response) == {"count": 8}
    table_client.upsert_entity.assert_called_once_with(
        entity={"PartitionKey": "visitor", "RowKey": "0", "Count": 8},
        mode=function_app.UpdateMode.REPLACE,
    )


def test_missing_counter_row_starts_at_one(monkeypatch):
    table_client = Mock()
    table_client.create_table.side_effect = ResourceExistsError("exists")
    table_client.get_entity.side_effect = ResourceNotFoundError("missing")

    table_client_class = Mock()
    table_client_class.from_connection_string.return_value = table_client

    monkeypatch.setenv("STORAGE_CONNECTION_STRING", "UseDevelopmentStorage=true")
    monkeypatch.setenv("TABLE_NAME", "Counter")
    monkeypatch.setattr(function_app, "TableClient", table_client_class)

    response = function_app.GetResumeCounter(make_request())

    assert response.status_code == 200
    assert response_json(response) == {"count": 1}
    table_client.upsert_entity.assert_called_once_with(
        entity={"PartitionKey": "visitor", "RowKey": "0", "Count": 1},
        mode=function_app.UpdateMode.REPLACE,
    )
