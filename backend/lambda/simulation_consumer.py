import json
import os
import sys
import traceback
from datetime import datetime, timezone
from decimal import Decimal

import boto3


# ---------------------------------------------------------
# Simulation imports
# ---------------------------------------------------------

SIMULATION_DIR = os.path.join(
    os.path.dirname(__file__),
    "simulation",
)

sys.path.insert(0, SIMULATION_DIR)

from scenario_time_step import run_scenario


# ---------------------------------------------------------
# DynamoDB
# ---------------------------------------------------------

AWS_REGION = os.environ.get(
    "AWS_REGION",
    "ap-south-1",
)

TABLE_NAME = os.environ.get(
    "AEGISTWIN_TABLE",
    "aegistwin-runs",
)

dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION,
)

runs_table = dynamodb.Table(TABLE_NAME)


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def now_iso():
    return datetime.now(timezone.utc).isoformat()


def to_decimal(value):
    if isinstance(value, Decimal):
        return value

    if value is None:
        return Decimal("0")

    return Decimal(str(value))


# ---------------------------------------------------------
# Request → simulation arguments
# ---------------------------------------------------------

def build_simulation_args(request):
    environment = request.get("environment", {})
    scenario = request.get("scenario", {})
    interventions = request.get("interventions", [])

    population_size = int(
        environment.get("population_size", 500)
    )

    region = environment.get(
        "region",
        "global",
    )

    blocked_nodes = scenario.get(
        "blocked_nodes",
        [],
    )

    blocked_node = (
        blocked_nodes[0]
        if blocked_nodes
        else None
    )

    block_time = scenario.get(
        "start_time"
    )

    if block_time is not None:
        block_time = float(block_time)

    capacity_overrides = {}
    edge_cost_multipliers = {}

    for intervention in interventions:

        intervention_type = intervention.get(
            "type"
        )

        if intervention_type == "flow_improvement":

            target = intervention.get(
                "target",
                "",
            )

            multiplier = intervention.get(
                "multiplier"
            )

            if (
                "->" not in target
                or multiplier is None
            ):
                continue

            source, destination = target.split(
                "->",
                1,
            )

            edge_key = tuple(
                sorted(
                    (
                        source.strip(),
                        destination.strip(),
                    )
                )
            )

            edge_cost_multipliers[
                edge_key
            ] = float(multiplier)

        elif intervention_type == "capacity_override":

            target = intervention.get(
                "target"
            )

            capacity = intervention.get(
                "capacity"
            )

            if (
                target
                and capacity is not None
            ):
                capacity_overrides[
                    target
                ] = int(capacity)

    return {
        "population_size": population_size,
        "region": region,
        "blocked_node": blocked_node,
        "block_time": block_time,
        "capacity_overrides": capacity_overrides,
        "edge_cost_multipliers": edge_cost_multipliers,
    }


# ---------------------------------------------------------
# Result
# ---------------------------------------------------------

def build_result(request, result):

    scenario = request.get(
        "scenario",
        {},
    )

    return {
        "run_id": (
            "run-"
            + datetime.now(timezone.utc).strftime(
                "%Y%m%d%H%M%S%f"
            )
        ),

        "status": "completed",

        "created_at": now_iso(),

        "project_id": request.get(
            "project_id",
            "unknown",
        ),

        "scenario": {
            "name": scenario.get(
                "name",
                "Unnamed Scenario",
            ),
            "hazard": scenario.get(
                "hazard",
                "unknown",
            ),
            "blocked_nodes": scenario.get(
                "blocked_nodes",
                [],
            ),
            "start_time": scenario.get(
                "start_time"
            ),
        },

        "metrics": {
            "population": result.get(
                "population",
                0,
            ),
            "completed": result.get(
                "completed",
                0,
            ),
            "failed": result.get(
                "failed",
                0,
            ),
            "remaining": result.get(
                "remaining",
                0,
            ),
            "completion_rate": (
                float(
                    result.get(
                        "completion_rate",
                        0,
                    )
                )
                * 100
            ),
            "failure_rate": (
                float(
                    result.get(
                        "failure_rate",
                        0,
                    )
                )
                * 100
            ),
            "minimum_evacuation_time": result.get(
                "minimum_evacuation_time",
                0,
            ),
            "average_evacuation_time": result.get(
                "average_evacuation_time",
                0,
            ),
            "maximum_evacuation_time": result.get(
                "maximum_evacuation_time",
                0,
            ),
            "reroutes": result.get(
                "reroute_count",
                0,
            ),
            "simulation_duration": result.get(
                "simulation_time",
                0,
            ),
        },

        "aws": {
            "service": "AWS Lambda",
            "trigger": "Amazon SQS",
            "region": AWS_REGION,
        },
    }


# ---------------------------------------------------------
# Save to DynamoDB
# ---------------------------------------------------------

def save_to_dynamodb(response):

    item = {
        "run_id": response["run_id"],
        "status": response["status"],
        "created_at": response["created_at"],
        "project_id": response["project_id"],

        "scenario": response["scenario"],

        "metrics": {
            key: to_decimal(value)
            for key, value in response["metrics"].items()
        },

        "aws": response["aws"],
    }

    runs_table.put_item(
        Item=item
    )

    print(
        f"RESULT STORED IN DYNAMODB: {TABLE_NAME}"
    )


# ---------------------------------------------------------
# Process SQS record
# ---------------------------------------------------------

def process_record(record):

    body = record.get(
        "body",
        "{}",
    )

    request = (
        json.loads(body)
        if isinstance(body, str)
        else body
    )

    print("=" * 60)
    print("AEGISTWIN SIMULATION CONSUMER")
    print("=" * 60)

    print(
        "Project:",
        request.get("project_id"),
    )

    print(
        "Scenario:",
        request.get(
            "scenario",
            {},
        ).get("name"),
    )

    args = build_simulation_args(
        request
    )

    print()
    print(
        "Running AegisTwin simulation..."
    )

    print(
        "Population:",
        args["population_size"],
    )

    print(
        "Region:",
        args["region"],
    )

    print(
        "Blocked node:",
        args["blocked_node"],
    )

    print(
        "Block time:",
        args["block_time"],
    )

    print(
        "Flow interventions:",
        len(
            args["edge_cost_multipliers"]
        ),
    )

    print(
        "Capacity interventions:",
        len(
            args["capacity_overrides"]
        ),
    )

    result = run_scenario(
        population_size=args[
            "population_size"
        ],
        region=args[
            "region"
        ],
        blocked_node=args[
            "blocked_node"
        ],
        block_time=args[
            "block_time"
        ],
        seed=42,
        capacity_overrides=args[
            "capacity_overrides"
        ],
        edge_cost_multipliers=args[
            "edge_cost_multipliers"
        ],
    )

    response = build_result(
        request,
        result,
    )

    print()
    print("=" * 60)
    print("SIMULATION COMPLETED")
    print("=" * 60)

    print(
        json.dumps(
            response,
            indent=2,
        )
    )

    save_to_dynamodb(
        response
    )

    return response


# ---------------------------------------------------------
# Lambda handler
# ---------------------------------------------------------

def handler(event, context):

    records = event.get(
        "Records",
        [],
    )

    print(
        f"Received {len(records)} SQS record(s)"
    )

    results = []

    for record in records:

        try:

            response = process_record(
                record
            )

            results.append(
                response
            )

        except Exception as exc:

            print(
                f"SIMULATION FAILED: "
                f"{type(exc).__name__}: {exc}"
            )

            traceback.print_exc()

            raise

    return {
        "statusCode": 200,
        "processed": len(results),
        "results": results,
    }