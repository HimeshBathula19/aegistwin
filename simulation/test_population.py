from campus import create_campus
from population import generate_population


def test_population_generation():

    campus = create_campus()

    population = generate_population(
        campus,
        100,
    )

    assert len(population) == 100

    assert len(
        {
            agent.agent_id
            for agent in population
        }
    ) == 100


if __name__ == "__main__":

    test_population_generation()

    print(
        "100-agent population test passed."
    )