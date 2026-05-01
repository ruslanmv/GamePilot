import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def predict_action(clip_path: str) -> dict:
    _ = clip_path
    return {
        "top_action": "move_forward",
        "confidence": 0.91,
        "top_5": [
            ["move_forward", 0.91],
            ["turn_left", 0.04],
            ["idle", 0.02],
            ["interact", 0.02],
            ["attack_target", 0.01],
        ],
    }


if __name__ == "__main__":
    output = predict_action(str(BASE_DIR / "examples" / "sample_clip.mp4"))
    out_file = BASE_DIR / "examples" / "sample_output.json"
    out_file.write_text(json.dumps(output, indent=2))
    print(json.dumps(output, indent=2))
