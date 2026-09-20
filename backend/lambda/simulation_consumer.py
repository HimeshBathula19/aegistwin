import json
import os
import sys
import traceback
from datetime import datetime, timezone


# Lambda package layout:
#
# /var/task/
# ├── simulation_consumer.py
# └── simulation/
#
SIMULATION_DIR = os.path.join(os.path.dirname(__file__), "simulation")

if os.path.isdir(SIMULATION_DIR):
    sys.path.insert(0, SIMULATION_DIR)


try:
    from scenario_time_step import run_scenario
except Exception as import_error:
    run_scenario = None
    IMPORT_ERROR = str(import_error)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def build_simulation_request(request):
    """
    Convert the public AegisTwin request contract into
    the arguments expected by run_scenario().
    """

    environment = request.get("environment", {})
    scenario = request.get("scenario", {})
    interventions = request.get("interventions", [])

    population_size = int(
        environment.get("population_size", 500)
    )

    region = environment.get("region", "global")

    blocked_nodes = scenario.get("blocked_nodes", [])
    blocked_node = blocked_nodes[0] if blocked_nodes else None

    block_time = scenario.get("start_time")

    if block_time is not None:
        block_time = float(block_time)

    capacity_overrides = {}
    edge_cost_multipliers = {}

    for intervention in interventions:
        intervention_type = intervention.get("type")

        if intervention_type == "flow_improvement":
            target = intervention.get("target", "")
            multiplier = intervention.get("multiplier")

            if "->" not in target or multiplier is None:
                continue

            source, destination = target.split("->", 1)

            edge_key = tuple(
                sorted((source.strip(), destination.strip()))
            )

            edge_cost_multipliers[edge_key] = float(multiplier)

        elif intervention_type == "capacity_override":
            target = intervention.get("target")
            capacity = intervention.get("capacity")

            if target and capacity is not None:
                capacity_overrides[target] = int(capacity)

    return {
        "population_size": population_size,
        "region": region,
        "blocked_node": blocked_node,
        "block_time": block_time,
        "capacity_overrides": capacity_overrides,
        "edge_cost_multipliers": edge_cost_multipliers,
    }


def build_response(request, result):
    scenario = request.get("scenario", {})

    completion_rate = float(
        result.get("completion_rate", 0.0)
    ) * 100

    failure_rate = float(
        result.get("failure_rate", 0.0)
    ) * 100

    return {
        "run_id": (
            f"aws-run-"
            f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        ),
        "status": "completed",
        "created_at": utc_now(),

        "project_id": request.get(
            "project_id",
            "unknown"
        ),

        "scenario": {
            "name": scenario.get(
                "name",
                "Unnamed Scenario"
            ),
            "hazard": scenario.get(
                "hazard",
                "unknown"
            ),
            "blocked_nodes": scenario.get(
                "blocked_nodes",
                []
            ),
            "start_time": scenario.get(
                "start_time"
            ),
        },

        "metrics": {
            "population": result.get(
                "population",
                0
            ),
            "completed": result.get(
                "completed",
                0
            ),
            "failed": result.get(
                "failed",
                0
            ),
            "remaining": result.get(
                "remaining",
                0
            ),
            "completion_rate": completion_rate,
            "failure_rate": failure_rate,
            "minimum_evacuation_time": result.get(
                "minimum_evacuation_time",
                0
            ),
            "average_evacuation_time": result.get(
                "average_evacuation_time",
                0
            ),
            "maximum_evacuation_time": result.get(
                "maximum_evacuation_time",
                0
            ),
            "reroutes": result.get(
                "reroute_count",
                0
            ),
            "simulation_duration": result.get(
                "simulation_time",
                0
            ),
        },

        "aws": {
            "service": "AWS Lambda",
            "trigger": "Amazon SQS",
            "region": os.environ.get(
                "AWS_REGION",
                "unknown"
            ),
        },
    }


def process_record(record):
    body = record.get("body", "{}")

    if isinstance(body, str):
        request = json.loads(body)
    else:
        request = body

    print("=" * 60)
    print("AEGISTWIN SIMULATION CONSUMER")
    print("=" * 60)

    print("Project:", request.get("project_id"))
    print(
        "Scenario:",
        request.get("scenario", {}).get("name")
    )

    simulation_args = build_simulation_request(request)

    print()
    print("Running AegisTwin simulation...")
    print(
        "Population:",
        simulation_args["population_size"]
    )
    print(
        "Region:",
        simulation_args["region"]
    )
    print(
        "Blocked node:",
        simulation_args["blocked_node"]
    )
    print(
        "Block time:",
        simulation_args["block_time"]
    )
    print(
        "Flow interventions:",
        len(simulation_args["edge_cost_multipliers"])
    )
    print(
        "Capacity interventions:",
        len(simulation_args["capacity_overrides"])
    )

    if run_scenario is None:
        raise RuntimeError(
            "Unable to import scenario_time_step.py: "
            + IMPORT_ERROR
        )

    result = run_scenario(
        population_size=simulation_args[
            "population_size"
        ],
        region=simulation_args[
            "region"
        ],
        blocked_node=simulation_args[
            "blocked_node"
        ],
        block_time=simulation_args[
            "block_time"
        ],
        seed=42,
        capacity_overrides=simulation_args[
            "capacity_overrides"
        ],
        edge_cost_multipliers=simulation_args[
            "edge_cost_multipliers"
        ],
    )

    response = build_response(
        request,
        result
    )

    print()
    print("=" * 60)
    print("SIMULATION COMPLETED")
    print("=" * 60)

    print(
        json.dumps(
            response,
            indent=2
        )
    )

    return response


def handler(event, context):
    """
    AWS Lambda entry point.

    Trigger:
        Amazon SQS
    """

    records = event.get("Records", [])

    print(
        f"Received {len(records)} SQS record(s)"
    )

    results = []

    for record in records:
        try:
            result = process_record(record)
            results.append(result)

        except Exception as exc:
            print()
            print("=" * 60)
            print("SIMULATION FAILED")
            print("=" * 60)

            print(
                f"{type(exc).__name__}: {exc}"
            )

            traceback.print_exc()

            raise

    return {
        "statusCode": 200,
        "processed": len(results),
        "results": results,
    }