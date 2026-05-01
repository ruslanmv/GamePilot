from gamepilot.app.models.imitation import ImitationRuntime
from gamepilot.app.models.transformer import TransformerRuntime


class RuntimeRegistry:
    def __init__(self) -> None:
        self.imitation = ImitationRuntime()
        self.transformer = TransformerRuntime()

    def predict(self, policy: str, state: dict, goal: str) -> str:
        if policy.startswith("imitation"):
            return self.imitation.predict(state, goal)
        if policy.startswith("transformer"):
            return self.transformer.predict(state, goal)
        return goal
