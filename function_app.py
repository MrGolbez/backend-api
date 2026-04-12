import json
import logging
import os

import azure.functions as func
from azure.core.exceptions import ResourceNotFoundError
from azure.data.tables import TableClient, UpdateMode

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="GetResumeCounter", methods=["GET", "OPTIONS"])
def GetResumeCounter(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("GetResumeCounter function triggered.")

    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }

    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=cors_headers)

    connection_string = os.environ.get("STORAGE_CONNECTION_STRING")
    table_name = os.environ.get("TABLE_NAME")

    if not connection_string or not table_name:
        logging.error("Required application settings are missing.")
        return func.HttpResponse(
            json.dumps({"error": "Server configuration error."}),
            status_code=500,
            mimetype="application/json",
            headers=cors_headers,
        )

    partition_key = "visitor"
    row_key = "0"

    try:
        table_client = TableClient.from_connection_string(
            conn_str=connection_string,
            table_name=table_name,
        )

        try:
            entity = table_client.get_entity(
                partition_key=partition_key,
                row_key=row_key,
            )
            current_count = int(entity.get("Count", 0))
        except ResourceNotFoundError:
            logging.warning("Counter row not found. Creating a new counter entry.")
            current_count = 0

        new_count = current_count + 1
        table_client.upsert_entity(
            entity={
                "PartitionKey": partition_key,
                "RowKey": row_key,
                "Count": new_count,
            },
            mode=UpdateMode.REPLACE,
        )

        return func.HttpResponse(
            json.dumps({"count": new_count}),
            status_code=200,
            mimetype="application/json",
            headers=cors_headers,
        )
    except Exception as exc:
        logging.error("Unexpected error updating visitor counter: %s", exc, exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": "An internal server error occurred."}),
            status_code=500,
            mimetype="application/json",
            headers=cors_headers,
        )
