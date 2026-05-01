# GamePilot Model Package Contract

A compatible model package should contain:

- `config.json`
- `model.safetensors`
- `action_labels.json`
- `mappings.yaml`
- `preprocessor_config.json`
- `README.md`

## Runtime contract
- Input: 128-dim state vector (`gamepilot.app.perception.state_builder.state_to_vector`).
- Output: action label index or action string.
- Policy metadata: `imitation_*` or `transformer_*` policy family.
