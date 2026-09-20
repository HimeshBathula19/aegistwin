import random
from dataclasses import dataclass
from agents import Agent


# ============================================================
# GLOBAL POPULATION PROFILES
# ============================================================

REGION_PROFILES = {
    "global": {
        "age_groups": [
            (0, 14, 0.25),
            (15, 24, 0.16),
            (25, 44, 0.27),
            (45, 64, 0.20),
            (65, 100, 0.12),
        ]
    },

    "india": {
        "age_groups": [
            (0, 14, 0.25),
            (15, 24, 0.18),
            (25, 44, 0.27),
            (45, 64, 0.19),
            (65, 100, 0.11),
        ]
    },

    "usa": {
        "age_groups": [
            (0, 14, 0.18),
            (15, 24, 0.13),
            (25, 44, 0.26),
            (45, 64, 0.25),
            (65, 100, 0.18),
        ]
    },

    "japan": {
        "age_groups": [
            (0, 14, 0.12),
            (15, 24, 0.10),
            (25, 44, 0.22),
            (45, 64, 0.28),
            (65, 100, 0.28),
        ]
    },

    "germany": {
        "age_groups": [
            (0, 14, 0.14),
            (15, 24, 0.10),
            (25, 44, 0.24),
            (45, 64, 0.27),
            (65, 100, 0.25),
        ]
    },
}


# ============================================================
# AGENT PROFILE
# ============================================================

@dataclass
class PopulationProfile:

    age: int

    mobility: str

    familiarity: str

    behavior: str

    group_size: int

    walking_speed: float

    reaction_time: float


# ============================================================
# AGE GENERATOR
# ============================================================

def generate_age(region: str):

    profile = REGION_PROFILES.get(
        region.lower(),
        REGION_PROFILES["global"],
    )

    groups = profile["age_groups"]

    random_value = random.random()

    cumulative = 0.0

    for minimum, maximum, probability in groups:

        cumulative += probability

        if random_value <= cumulative:

            return random.randint(
                minimum,
                maximum,
            )

    return random.randint(18, 60)


# ============================================================
# MOBILITY MODEL
# ============================================================

def generate_mobility(age):

    value = random.random()

    if age >= 70:

        if value < 0.25:
            return "reduced"

        return "normal"

    if age >= 60:

        if value < 0.12:
            return "reduced"

        return "normal"

    if value < 0.04:
        return "assisted"

    return "normal"


# ============================================================
# WALKING SPEED
# ============================================================

def generate_walking_speed(
    age,
    mobility,
):

    if mobility == "assisted":

        return random.uniform(
            0.45,
            0.75,
        )

    if mobility == "reduced":

        return random.uniform(
            0.65,
            1.00,
        )

    if age < 18:

        return random.uniform(
            0.90,
            1.30,
        )

    if age >= 65:

        return random.uniform(
            0.85,
            1.20,
        )

    return random.uniform(
        1.05,
        1.55,
    )


# ============================================================
# REACTION TIME
# ============================================================

def generate_reaction_time(
    age,
    mobility,
):

    base = random.uniform(
        3.0,
        7.0,
    )

    if age >= 65:

        base += random.uniform(
            1.0,
            3.0,
        )

    if mobility == "assisted":

        base += random.uniform(
            1.0,
            2.5,
        )

    return round(
        base,
        2,
    )


# ============================================================
# BEHAVIOR
# ============================================================

def generate_behavior():

    value = random.random()

    if value < 0.15:
        return "cautious"

    if value < 0.30:
        return "hesitant"

    if value < 0.85:
        return "normal"

    return "fast_responder"


# ============================================================
# FAMILIARITY
# ============================================================

def generate_familiarity():

    value = random.random()

    if value < 0.20:
        return "low"

    if value < 0.70:
        return "medium"

    return "high"


# ============================================================
# GROUP SIZE
# ============================================================

def generate_group_size():

    value = random.random()

    if value < 0.70:
        return 1

    if value < 0.90:
        return 2

    if value < 0.97:
        return 3

    return random.randint(
        4,
        6,
    )


# ============================================================
# PROFILE GENERATOR
# ============================================================

def generate_profile(region="global"):

    age = generate_age(region)

    mobility = generate_mobility(
        age
    )

    familiarity = generate_familiarity()

    behavior = generate_behavior()

    group_size = generate_group_size()

    walking_speed = generate_walking_speed(
        age,
        mobility,
    )

    reaction_time = generate_reaction_time(
        age,
        mobility,
    )

    # Behavior influences response slightly.
    if behavior == "cautious":

        reaction_time += 1.5

    elif behavior == "hesitant":

        reaction_time += 2.5

    elif behavior == "fast_responder":

        reaction_time -= 1.0

    reaction_time = max(
        1.0,
        round(
            reaction_time,
            2,
        ),
    )

    return PopulationProfile(
        age=age,
        mobility=mobility,
        familiarity=familiarity,
        behavior=behavior,
        group_size=group_size,
        walking_speed=round(
            walking_speed,
            2,
        ),
        reaction_time=reaction_time,
    )


# ============================================================
# POPULATION GENERATOR
# ============================================================

def generate_population(
    campus,
    population_size: int,
    region="global",
    seed=None,
):

    if population_size <= 0:

        raise ValueError(
            "Population size must be greater than zero."
        )

    if seed is not None:

        random.seed(seed)

    starting_locations = [
        node
        for node, data in campus.nodes(data=True)
        if data["type"] == "room"
    ]

    population = []

    for agent_id in range(
        1,
        population_size + 1,
    ):

        start_location = random.choice(
            starting_locations
        )

        profile = generate_profile(
            region
        )

        agent = Agent(
            agent_id=agent_id,
            start_location=start_location,
            destination="",
            speed=profile.walking_speed,
            reaction_time=profile.reaction_time,
        )

        # Attach additional synthetic
        # population attributes.
        agent.age = profile.age
        agent.mobility = profile.mobility
        agent.familiarity = profile.familiarity
        agent.behavior = profile.behavior
        agent.group_size = profile.group_size
        agent.region = region

        population.append(
            agent
        )

    return population


# ============================================================
# INSPECTION
# ============================================================

def print_population_sample(
    population,
    count=10,
):

    print()
    print("=" * 90)
    print("AEGISTWIN SYNTHETIC POPULATION")
    print("=" * 90)

    print(
        f"{'ID':<6}"
        f"{'AGE':<7}"
        f"{'MOBILITY':<12}"
        f"{'BEHAVIOR':<16}"
        f"{'FAMILIARITY':<15}"
        f"{'SPEED':<10}"
        f"{'REACTION':<10}"
    )

    print("-" * 90)

    for agent in population[:count]:

        print(
            f"{agent.agent_id:<6}"
            f"{agent.age:<7}"
            f"{agent.mobility:<12}"
            f"{agent.behavior:<16}"
            f"{agent.familiarity:<15}"
            f"{agent.speed:<10.2f}"
            f"{agent.reaction_time:<10.2f}"
        )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    from campus import create_campus

    campus = create_campus()

    population = generate_population(
        campus,
        population_size=1000,
        region="japan",
        seed=42,
    )

    print_population_sample(
        population,
        count=15,
    )

    print()
    print(
        f"Generated synthetic population: "
        f"{len(population)}"
    )