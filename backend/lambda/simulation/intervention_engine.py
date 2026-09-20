from diagnosis_engine import ACTIONABLE_TYPES


# ============================================================
# INTERVENTION ENGINE
# ============================================================

class InterventionGenerator:
    """
    Converts simulation-derived diagnosis findings into
    candidate interventions.

    Important:
    These are candidate configurations for simulation.
    They are not real-world emergency instructions.
    """

    def __init__(
        self,
        campus,
        blocked_infrastructure=None,
    ):

        self.campus = campus

        self.blocked_infrastructure = (
            blocked_infrastructure
        )

    # ========================================================
    # EDGE NORMALIZATION
    # ========================================================

    def normalize_edge(
        self,
        source,
        destination,
    ):
        """
        Normalize an undirected campus connection.

        This prevents:
            A -> B
        and
            B -> A

        from being treated as separate interventions.
        """

        if str(source) <= str(destination):

            return (
                source,
                destination,
            )

        return (
            destination,
            source,
        )

    # ========================================================
    # VALID EDGE
    # ========================================================

    def is_valid_edge(
        self,
        source,
        destination,
    ):
        """
        Check whether an edge can actually be used
        as an intervention candidate.
        """

        if source not in self.campus:
            return False

        if destination not in self.campus:
            return False

        if (
            self.blocked_infrastructure
            and (
                source
                == self.blocked_infrastructure
                or destination
                == self.blocked_infrastructure
            )
        ):

            return False

        return True

    # ========================================================
    # CAPACITY INTERVENTIONS
    # ========================================================

    def generate_capacity_interventions(
        self,
        finding,
    ):

        location = finding[
            "location"
        ]

        if location not in self.campus:
            return []

        if (
            location
            == self.blocked_infrastructure
        ):
            return []

        current_capacity = self.campus.nodes[
            location
        ].get(
            "capacity",
            0,
        )

        if current_capacity <= 0:
            return []

        interventions = []

        # ----------------------------------------------------
        # 25% increase
        # ----------------------------------------------------

        capacity_25 = int(
            current_capacity * 1.25
        )

        interventions.append(
            {
                "type":
                    "capacity_increase",

                "target":
                    location,

                "changes":
                    {
                        "capacity_overrides":
                            {
                                location:
                                    capacity_25
                            }
                    },

                "reason":
                    f"Increase {location} "
                    f"capacity by 25%."
            }
        )

        # ----------------------------------------------------
        # 50% increase
        # ----------------------------------------------------

        capacity_50 = int(
            current_capacity * 1.50
        )

        interventions.append(
            {
                "type":
                    "capacity_increase",

                "target":
                    location,

                "changes":
                    {
                        "capacity_overrides":
                            {
                                location:
                                    capacity_50
                            }
                    },

                "reason":
                    f"Increase {location} "
                    f"capacity by 50%."
            }
        )

        return interventions

    # ========================================================
    # FLOW INTERVENTIONS
    # ========================================================

    def generate_flow_interventions(
        self,
        finding,
    ):

        location = finding[
            "location"
        ]

        if location not in self.campus:
            return []

        if (
            location
            == self.blocked_infrastructure
        ):
            return []

        interventions = []

        neighbors = list(
            self.campus.neighbors(
                location
            )
        )

        for neighbor in neighbors:

            if not self.is_valid_edge(
                location,
                neighbor,
            ):
                continue

            edge = self.normalize_edge(
                location,
                neighbor,
            )

            interventions.append(
                {
                    "type":
                        "flow_improvement",

                    "target":
                        location,

                    "edge":
                        edge,

                    "changes":
                        {
                            "edge_cost_multipliers":
                                {
                                    edge:
                                        0.75
                                }
                        },

                    "reason":
                        f"Improve simulated flow "
                        f"through {edge[0]} → "
                        f"{edge[1]}."
                }
            )

        return interventions

    # ========================================================
    # ALTERNATE ROUTE INTERVENTIONS
    # ========================================================

    def generate_alternate_route_interventions(
        self,
        finding,
    ):

        location = finding[
            "location"
        ]

        if location not in self.campus:
            return []

        if (
            location
            == self.blocked_infrastructure
        ):
            return []

        interventions = []

        neighbors = list(
            self.campus.neighbors(
                location
            )
        )

        for neighbor in neighbors:

            if not self.is_valid_edge(
                location,
                neighbor,
            ):
                continue

            edge = self.normalize_edge(
                location,
                neighbor,
            )

            interventions.append(
                {
                    "type":
                        "alternate_route",

                    "target":
                        location,

                    "edge":
                        edge,

                    "changes":
                        {
                            "edge_cost_multipliers":
                                {
                                    edge:
                                        0.85
                                }
                        },

                    "reason":
                        f"Reduce simulated travel "
                        f"cost on connection "
                        f"{edge[0]} → {edge[1]}."
                }
            )

        return interventions

    # ========================================================
    # GENERATE FOR ONE FINDING
    # ========================================================

    def generate_for_finding(
        self,
        finding,
    ):

        if (
            finding["node_type"]
            not in ACTIONABLE_TYPES
        ):

            return []

        location = finding[
            "location"
        ]

        if (
            location
            == self.blocked_infrastructure
        ):

            return []

        interventions = []

        risk_level = finding[
            "risk_level"
        ]

        dependency = finding.get(
            "scenario_dependency",
            0.0,
        )

        # ----------------------------------------------------
        # Capacity
        # ----------------------------------------------------

        if risk_level in {
            "CRITICAL",
            "HIGH",
        }:

            interventions.extend(
                self.generate_capacity_interventions(
                    finding
                )
            )

        # ----------------------------------------------------
        # Flow improvement
        # ----------------------------------------------------

        if dependency >= 0.50:

            interventions.extend(
                self.generate_flow_interventions(
                    finding
                )
            )

        # ----------------------------------------------------
        # Alternate route
        # ----------------------------------------------------

        if risk_level in {
            "CRITICAL",
            "HIGH",
        }:

            interventions.extend(
                self.generate_alternate_route_interventions(
                    finding
                )
            )

        return interventions

    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    def deduplicate(
        self,
        candidates,
    ):

        unique = []

        seen = set()

        for candidate in candidates:

            changes = candidate.get(
                "changes",
                {},
            )

            capacity_changes = tuple(
                sorted(
                    changes.get(
                        "capacity_overrides",
                        {},
                    ).items()
                )
            )

            edge_changes = []

            for edge, multiplier in (
                changes.get(
                    "edge_cost_multipliers",
                    {},
                ).items()
            ):

                normalized_edge = (
                    self.normalize_edge(
                        edge[0],
                        edge[1],
                    )
                )

                edge_changes.append(
                    (
                        normalized_edge,
                        multiplier,
                    )
                )

            edge_changes = tuple(
                sorted(
                    edge_changes,
                    key=str,
                )
            )

            key = (
                candidate["type"],
                candidate["target"],
                capacity_changes,
                edge_changes,
            )

            if key in seen:
                continue

            seen.add(key)

            unique.append(
                candidate
            )

        return unique

    # ========================================================
    # GENERATE SYSTEM-WIDE CANDIDATES
    # ========================================================

    def generate(
        self,
        diagnosis,
        max_findings=3,
    ):
        """
        Generate candidate interventions from the
        highest-priority actionable findings.
        """

        candidates = []

        findings = diagnosis.get(
            "actionable_findings",
            [],
        )

        # ----------------------------------------------------
        # Never generate interventions for the failed node.
        # ----------------------------------------------------

        findings = [
            finding
            for finding in findings
            if finding["location"]
            != self.blocked_infrastructure
        ]

        findings = findings[
            :max_findings
        ]

        for finding in findings:

            candidates.extend(
                self.generate_for_finding(
                    finding
                )
            )

        candidates = self.deduplicate(
            candidates
        )

        # ----------------------------------------------------
        # Assign stable intervention IDs.
        # ----------------------------------------------------

        for index, candidate in enumerate(
            candidates,
            start=1,
        ):

            candidate[
                "intervention_id"
            ] = (
                f"INT-{index:03d}"
            )

        return candidates


# ============================================================
# PRINT INTERVENTIONS
# ============================================================

def print_interventions(
    interventions,
):

    print()

    print("=" * 110)

    print(
        "AEGISTWIN INTERVENTION GENERATOR"
    )

    print("=" * 110)

    print(
        f"Candidate interventions: "
        f"{len(interventions)}"
    )

    print()

    for intervention in interventions:

        print(
            f"{intervention['intervention_id']} | "
            f"{intervention['type']:<20} | "
            f"{intervention['target']:<20}"
        )

        print(
            f"    Reason: "
            f"{intervention['reason']}"
        )

        print(
            f"    Changes: "
            f"{intervention['changes']}"
        )

        print()


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    from campus import create_campus
    from diagnosis_engine import diagnose_scenario
    from scenario_time_step import run_scenario

    POPULATION_SIZE = 500
    REGION = "global"
    SEED = 42

    BLOCKED_INFRASTRUCTURE = (
        "staircase_a"
    )

    EMERGENCY_TIME = 5

    print(
        "Running baseline..."
    )

    baseline = run_scenario(
        population_size=POPULATION_SIZE,
        region=REGION,
        blocked_node=None,
        block_time=None,
        seed=SEED,
    )

    print(
        "Running disruption..."
    )

    scenario = run_scenario(
        population_size=POPULATION_SIZE,
        region=REGION,
        blocked_node=BLOCKED_INFRASTRUCTURE,
        block_time=EMERGENCY_TIME,
        seed=SEED,
    )

    diagnosis = diagnose_scenario(
        baseline,
        scenario,
    )

    campus = create_campus()

    generator = InterventionGenerator(
        campus,
        blocked_infrastructure=(
            BLOCKED_INFRASTRUCTURE
        ),
    )

    interventions = generator.generate(
        diagnosis,
        max_findings=3,
    )

    print_interventions(
        interventions
    )