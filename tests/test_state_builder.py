from gamepilot.app.perception.state_builder import build_state, state_to_vector


def test_state_builder_and_vector():
    state = build_state({"hp": 50, "enemy_near": True})
    vec = state_to_vector(state)
    assert state["hp"] == 50
    assert len(vec) == 128
    assert vec[1] == 1.0
