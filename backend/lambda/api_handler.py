import base64
import json
import os
from decimal import Decimal

import boto3


AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")
SQS_QUEUE_URL = os.environ["SQS_QUEUE_URL"]
TABLE_NAME = os.environ.get("AEGISTWIN_TABLE", "aegistwin-runs")

sqs = boto3.client("sqs", region_name=AWS_REGION)
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
runs_table = dynamodb.Table(TABLE_NAME)

# Amazon Location Service Places V2
geo_places = boto3.client(
    "geo-places",
    region_name=AWS_REGION,
)


def decimal_to_python(value):
    if isinstance(value, Decimal):
        if value % 1 == 0:
            return int(value)
        return float(value)

    if isinstance(value, dict):
        return {
            key: decimal_to_python(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [
            decimal_to_python(item)
            for item in value
        ]

    return value


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "content-type": "application/json",
            "access-control-allow-origin": "*",
            "access-control-allow-methods": "GET,POST,OPTIONS",
            "access-control-allow-headers": "content-type",
        },
        "body": json.dumps(body),
    }


def parse_body(event):
    body = event.get("body")

    if not body:
        return {}

    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8")

    if isinstance(body, dict):
        return body

    return json.loads(body)


def get_query_parameters(event):
    parameters = event.get("queryStringParameters") or {}

    # API Gateway HTTP API
    if isinstance(parameters, dict):
        return parameters

    return {}


def handle_simulation(event):
    try:
        request = parse_body(event)
    except json.JSONDecodeError:
        return response(
            400,
            {"error": "Request body must contain valid JSON."},
        )

    if not isinstance(request, dict):
        return response(
            400,
            {"error": "Request body must be a JSON object."},
        )

    if "environment" not in request:
        return response(
            400,
            {"error": "Missing environment."},
        )

    if "scenario" not in request:
        return response(
            400,
            {"error": "Missing scenario."},
        )

    message = sqs.send_message(
        QueueUrl=SQS_QUEUE_URL,
        MessageBody=json.dumps(request),
    )

    return response(
        202,
        {
            "status": "accepted",
            "message_id": message["MessageId"],
            "message": "Simulation submitted successfully.",
        },
    )


def handle_runs():
    result = runs_table.scan(Limit=25)

    items = [
        decimal_to_python(item)
        for item in result.get("Items", [])
    ]

    items.sort(
        key=lambda item: item.get("created_at", ""),
        reverse=True,
    )

    return response(
        200,
        {
            "count": len(items),
            "runs": items,
        },
    )


def simplify_place(place):
    address = place.get("Address") or {}

    return {
        "place_id": place.get("PlaceId"),
        "type": place.get("PlaceType"),
        "name": place.get("Title"),
        "position": place.get("Position"),
        "map_view": place.get("MapView"),
        "address": {
            "label": address.get("Label"),
            "country": (address.get("Country") or {}).get("Name"),
            "country_code": (address.get("Country") or {}).get("Code2"),
            "region": (address.get("Region") or {}).get("Name"),
            "sub_region": (address.get("SubRegion") or {}).get("Name"),
            "locality": address.get("Locality"),
            "district": address.get("District"),
            "sub_district": address.get("SubDistrict"),
            "postal_code": address.get("PostalCode"),
            "street": address.get("Street"),
        },
        "categories": place.get("Categories", []),
        "contacts": place.get("Contacts", []),
        "access_points": place.get("AccessPoints", []),
    }


def handle_place_search(event):
    query_parameters = get_query_parameters(event)

    query = (
        query_parameters.get("q")
        or query_parameters.get("query")
        or ""
    ).strip()

    if not query:
        return response(
            400,
            {
                "error": "Missing search query.",
                "message": "Use /places/search?q=your place",
            },
        )

    try:
        result = geo_places.search_text(
            QueryText=query,
            MaxResults=8,
            BiasPosition=[78.4867, 17.3850],
            Language="en",
            IntendedUse="SingleUse",
            AdditionalFeatures=[
                "Access",
                "Contact",
            ],
        )

        places = [
            simplify_place(item)
            for item in result.get("ResultItems", [])
        ]

        return response(
            200,
            {
                "query": query,
                "count": len(places),
                "places": places,
            },
        )

    except Exception as exc:
        print(
            "Amazon Location search error:",
            repr(exc),
        )

        return response(
            500,
            {
                "error": "Location search failed.",
                "message": str(exc),
            },
        )

def handler(event, context):
    request_context = event.get("requestContext", {})
    http = request_context.get("http", {})

    method = http.get(
        "method",
        event.get("httpMethod", "GET"),
    )

    path = event.get("rawPath")

    if not path:
        path = event.get("path", "/")

    print(f"API request: {method} {path}")

    if method == "OPTIONS":
        return response(204, {})

    if method == "GET" and path == "/places/search":
        return handle_place_search(event)

    if method == "POST" and path == "/simulate":
        return handle_simulation(event)

    if method == "GET" and path == "/runs":
        return handle_runs()

    if method == "GET" and path == "/health":
        return response(
            200,
            {
                "status": "ok",
                "service": "AegisTwin API",
                "region": AWS_REGION,
            },
        )

    return response(
        404,
        {
            "error": "Route not found.",
            "path": path,
        },
    )