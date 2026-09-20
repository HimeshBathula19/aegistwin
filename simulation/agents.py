from dataclasses import dataclass, field
from typing import List


@dataclass
class Agent:
    """
    Represents one simulated person inside AegisTwin.
    """

    agent_id: int
    start_location: str
    destination: str

    speed: float = 1.2
    reaction_time: float = 5.0

    route: List[str] = field(default_factory=list)

    current_location: str = ""
    completed: bool = False
    travel_time: float = 0.0

    def __post_init__(self):
        self.current_location = self.start_location

    def assign_route(self, route: List[str]):
        self.route = route

    def calculate_travel_time(self, route_cost: float):
        if self.speed <= 0:
            raise ValueError(
                "Agent speed must be greater than zero."
            )

        movement_time = route_cost / self.speed

        self.travel_time = (
            self.reaction_time +
            movement_time
        )

        return self.travel_time

    def complete(self):
        self.current_location = self.destination
        self.completed = True

    def summary(self):
        return {
            "agent_id": self.agent_id,
            "start": self.start_location,
            "destination": self.destination,
            "speed": self.speed,
            "reaction_time": self.reaction_time,
            "route": self.route,
            "travel_time": round(self.travel_time, 2),
            "completed": self.completed,
        }