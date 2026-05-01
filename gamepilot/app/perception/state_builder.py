def build_state(detections: dict) -> dict:
    return {
        "hp": int(detections.get("hp", 100)),
        "enemy_near": bool(detections.get("enemy_near", False)),
        "loot_visible": bool(detections.get("loot_visible", False)),
        "npc_visible": bool(detections.get("npc_visible", False)),
        "quest_marker": detections.get("quest_marker", "unknown"),
        "stuck": bool(detections.get("stuck", False)),
        "quest_changed": bool(detections.get("quest_changed", False)),
    }


def state_to_vector(state: dict) -> list[float]:
    vector = [0.0] * 128
    vector[0] = float(state["hp"]) / 100.0
    vector[1] = 1.0 if state["enemy_near"] else 0.0
    vector[2] = 1.0 if state["loot_visible"] else 0.0
    vector[3] = 1.0 if state["npc_visible"] else 0.0
    vector[4] = 1.0 if state["stuck"] else 0.0
    return vector
