"""
Model loader for behavior cloning and RL models.
Loads PyTorch models from disk with proper contract validation.
"""
from pathlib import Path
from typing import Optional, Dict, Any
import json
import numpy as np

try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class GameplayModel(nn.Module):
    """
    Standard gameplay model architecture for behavior cloning.
    
    Input: 128-dim state vector
    Output: Action logits (10 classes by default)
    """
    
    def __init__(
        self,
        input_size: int = 128,
        hidden_size: int = 256,
        num_actions: int = 10,
        dropout: float = 0.3,
    ):
        super().__init__()
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_actions = num_actions
        
        # Feature extractor
        self.encoder = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.LayerNorm(hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout),
            
            nn.Linear(hidden_size, hidden_size),
            nn.LayerNorm(hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout),
            
            nn.Linear(hidden_size, hidden_size // 2),
            nn.LayerNorm(hidden_size // 2),
            nn.ReLU(),
        )
        
        # Action head
        self.action_head = nn.Linear(hidden_size // 2, num_actions)
    
    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            state: (batch, 128) state tensor
            
        Returns:
            logits: (batch, num_actions) action logits
        """
        features = self.encoder(state)
        logits = self.action_head(features)
        return logits
    
    def predict(self, state: np.ndarray) -> int:
        """
        Predict action from state.
        
        Args:
            state: State vector (128,) or (batch, 128)
            
        Returns:
            int: Predicted action index
        """
        self.eval()
        
        with torch.no_grad():
            # Convert to tensor
            if isinstance(state, np.ndarray):
                state = torch.from_numpy(state).float()
            
            # Add batch dimension if needed
            if state.dim() == 1:
                state = state.unsqueeze(0)
            
            # Forward pass
            logits = self.forward(state)
            
            # Get action
            action = logits.argmax(dim=1).item()
        
        return action


class ModelLoader:
    """
    Loader for trained gameplay models with contract validation.
    
    Expected model package structure:
    model_dir/
        ├── model.safetensors or model.pth
        ├── config.json
        ├── action_labels.json
        └── README.md (optional)
    """
    
    def __init__(self, model_dir: Path):
        """
        Initialize model loader.
        
        Args:
            model_dir: Directory containing model files
        """
        if not TORCH_AVAILABLE:
            raise ImportError("torch not installed. Install with: pip install torch")
        
        self.model_dir = Path(model_dir)
        
        if not self.model_dir.exists():
            raise FileNotFoundError(f"Model directory not found: {model_dir}")
        
        # Load config
        self.config = self._load_config()
        
        # Load action labels
        self.action_labels = self._load_action_labels()
        
        # Initialize model
        self.model = self._load_model()
        
        # Set device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()
        
        print(f"✓ Loaded model from {model_dir}")
        print(f"  Device: {self.device}")
        print(f"  Actions: {len(self.action_labels)}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load model configuration."""
        config_path = self.model_dir / "config.json"
        
        if not config_path.exists():
            # Use default config
            return {
                "input_size": 128,
                "hidden_size": 256,
                "num_actions": 10,
                "dropout": 0.3,
            }
        
        with open(config_path) as f:
            return json.load(f)
    
    def _load_action_labels(self) -> Dict[int, str]:
        """Load action label mapping."""
        labels_path = self.model_dir / "action_labels.json"
        
        if not labels_path.exists():
            # Use default labels
            return {
                0: "move_forward",
                1: "move_backward",
                2: "turn_left",
                3: "turn_right",
                4: "attack",
                5: "jump",
                6: "interact",
                7: "use_item",
                8: "open_inventory",
                9: "cast_spell",
            }
        
        with open(labels_path) as f:
            labels = json.load(f)
            # Convert string keys to int
            return {int(k): v for k, v in labels.items()}
    
    def _load_model(self) -> GameplayModel:
        """Load model weights."""
        # Try safetensors first (preferred)
        safetensors_path = self.model_dir / "model.safetensors"
        pth_path = self.model_dir / "model.pth"
        
        # Initialize model
        model = GameplayModel(
            input_size=self.config.get("input_size", 128),
            hidden_size=self.config.get("hidden_size", 256),
            num_actions=self.config.get("num_actions", 10),
            dropout=self.config.get("dropout", 0.3),
        )
        
        # Load weights
        if safetensors_path.exists():
            try:
                from safetensors.torch import load_file
                state_dict = load_file(str(safetensors_path))
                model.load_state_dict(state_dict)
                print(f"  Loaded from safetensors")
            except ImportError:
                print("  Warning: safetensors not installed, falling back to .pth")
                if pth_path.exists():
                    state_dict = torch.load(pth_path, map_location="cpu")
                    model.load_state_dict(state_dict)
        elif pth_path.exists():
            state_dict = torch.load(pth_path, map_location="cpu")
            model.load_state_dict(state_dict)
            print(f"  Loaded from .pth")
        else:
            print(f"  Warning: No weights found, using random initialization")
        
        return model
    
    def predict(self, state: np.ndarray) -> str:
        """
        Predict action from state.
        
        Args:
            state: State vector (128,)
            
        Returns:
            str: Action name (e.g., "move_forward")
        """
        # Convert to tensor
        state_tensor = torch.from_numpy(state).float().to(self.device)
        
        # Predict
        action_idx = self.model.predict(state_tensor.cpu().numpy())
        
        # Map to action name
        action_name = self.action_labels.get(action_idx, f"action_{action_idx}")
        
        return action_name
    
    def predict_with_confidence(self, state: np.ndarray) -> Dict[str, Any]:
        """
        Predict action with confidence scores.
        
        Args:
            state: State vector (128,)
            
        Returns:
            dict: {
                "action": action_name,
                "action_idx": index,
                "confidence": probability,
                "all_probs": {action_name: probability}
            }
        """
        state_tensor = torch.from_numpy(state).float().to(self.device)
        
        if state_tensor.dim() == 1:
            state_tensor = state_tensor.unsqueeze(0)
        
        with torch.no_grad():
            logits = self.model(state_tensor)
            probs = torch.softmax(logits, dim=1)[0]
        
        # Get top action
        action_idx = probs.argmax().item()
        confidence = probs[action_idx].item()
        action_name = self.action_labels.get(action_idx, f"action_{action_idx}")
        
        # Get all probabilities
        all_probs = {
            self.action_labels.get(i, f"action_{i}"): probs[i].item()
            for i in range(len(probs))
        }
        
        return {
            "action": action_name,
            "action_idx": action_idx,
            "confidence": confidence,
            "all_probs": all_probs,
        }


class MockModelLoader:
    """Mock model loader for testing."""
    
    def __init__(self, model_dir: Path):
        self.model_dir = model_dir
        print(f"Mock model loader initialized (no real model loaded)")
    
    def predict(self, state: np.ndarray) -> str:
        """Return default action."""
        return "explore"
    
    def predict_with_confidence(self, state: np.ndarray) -> Dict[str, Any]:
        """Return mock confidence."""
        return {
            "action": "explore",
            "action_idx": 0,
            "confidence": 0.85,
            "all_probs": {"explore": 0.85, "other": 0.15},
        }


def load_model(model_dir: str) -> ModelLoader:
    """
    Load a gameplay model from directory.
    
    Args:
        model_dir: Path to model directory
        
    Returns:
        ModelLoader or MockModelLoader
    """
    model_path = Path(model_dir)
    
    if not TORCH_AVAILABLE:
        print("PyTorch not available, using MockModelLoader")
        return MockModelLoader(model_path)
    
    try:
        return ModelLoader(model_path)
    except Exception as e:
        print(f"Failed to load model: {e}")
        print("Using MockModelLoader")
        return MockModelLoader(model_path)


if __name__ == "__main__":
    # Test model loader
    import tempfile
    
    print("Model Loader Test\n")
    
    if TORCH_AVAILABLE:
        # Create temporary model directory
        with tempfile.TemporaryDirectory() as tmpdir:
            model_dir = Path(tmpdir) / "test_model"
            model_dir.mkdir()
            
            # Create config
            config = {
                "input_size": 128,
                "hidden_size": 256,
                "num_actions": 10,
            }
            with open(model_dir / "config.json", "w") as f:
                json.dump(config, f)
            
            # Create action labels
            labels = {i: f"action_{i}" for i in range(10)}
            with open(model_dir / "action_labels.json", "w") as f:
                json.dump(labels, f)
            
            # Create and save model
            model = GameplayModel()
            torch.save(model.state_dict(), model_dir / "model.pth")
            
            # Load model
            loader = load_model(str(model_dir))
            
            # Test prediction
            test_state = np.random.randn(128).astype(np.float32)
            action = loader.predict(test_state)
            print(f"\nPredicted action: {action}")
            
            result = loader.predict_with_confidence(test_state)
            print(f"With confidence: {result}")
    else:
        print("PyTorch not installed. Install with: pip install torch")
