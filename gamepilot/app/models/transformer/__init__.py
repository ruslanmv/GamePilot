class TransformerRuntime:
    def predict(self, state: dict, goal: str) -> str:
        _ = state
        return f"{goal}_action"
