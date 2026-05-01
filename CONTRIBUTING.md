# Contributing to GamePilot

Thank you for your interest in contributing to GamePilot! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the project goals
- Follow ethical AI research practices

## Getting Started

### Prerequisites

- Python 3.10 or 3.11
- Git
- Basic understanding of AI/ML, computer vision, or game automation

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/gamepilot.git
cd gamepilot

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

- Write clear, documented code
- Follow PEP 8 style guide
- Add docstrings to all functions/classes
- Include type hints where appropriate

### 3. Write Tests

```bash
# Create test file
touch tests/test_your_feature.py

# Write tests
pytest tests/test_your_feature.py -v
```

### 4. Run Quality Checks

```bash
# Format code
black gamepilot tests

# Lint
ruff check gamepilot tests

# Type check
mypy gamepilot

# Run all tests
pytest tests/ -v --cov=gamepilot
```

### 5. Commit Your Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add YOLO detector for quest markers

- Implement quest marker detection
- Add confidence threshold tuning
- Update state builder integration
- Add unit tests
"
```

**Commit Message Format:**

```
<type>: <short description>

<detailed description>

<footer>
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

### 6. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create PR on GitHub
```

## Areas for Contribution

### High Priority

1. **Perception Improvements**
   - Better object detection models
   - OCR accuracy improvements
   - Game-specific detectors

2. **Model Training**
   - Behavior cloning datasets
   - Training pipelines
   - Model evaluation metrics

3. **Game Profiles**
   - Configuration templates for popular games
   - HUD region definitions
   - Action mappings

4. **Documentation**
   - Tutorial videos
   - Example notebooks
   - API documentation

### Medium Priority

5. **Frontend Development**
   - React UI components
   - Real-time visualization
   - Configuration interface

6. **Testing**
   - Integration tests
   - Performance benchmarks
   - Edge case coverage

7. **Safety Features**
   - Anti-cheat detection
   - Session monitoring
   - Ethical guidelines

## Code Style Guidelines

### Python

```python
# Good: Clear, documented function
def detect_enemies(
    frame: np.ndarray,
    confidence_threshold: float = 0.5
) -> List[Detection]:
    """
    Detect enemies in a game frame.
    
    Args:
        frame: RGB image (H, W, 3)
        confidence_threshold: Minimum confidence for detection
        
    Returns:
        List of Detection objects
    """
    # Implementation
    pass

# Bad: No types, no docs
def detect(f, t):
    # What does this do?
    pass
```

### File Organization

```
gamepilot/
├── app/
│   ├── perception/      # Computer vision
│   ├── decision/        # Planning & rules
│   ├── executor/        # Input control
│   ├── models/          # ML models
│   └── api/             # FastAPI server
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
└── docs/
```

## Testing Guidelines

### Unit Tests

```python
import pytest
from gamepilot.app.perception.detector import YOLODetector

def test_detector_initialization():
    """Test detector can be initialized."""
    detector = YOLODetector()
    assert detector is not None

def test_detector_on_sample_frame():
    """Test detector works on sample input."""
    detector = YOLODetector()
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    detections = detector.detect(frame)
    assert isinstance(detections, dict)
    assert "enemy_near" in detections
```

### Integration Tests

```python
def test_full_pipeline(sample_video):
    """Test complete perception → decision → execution pipeline."""
    # Setup
    orchestrator = Orchestrator()
    
    # Run
    result = orchestrator.run_demo(sample_video)
    
    # Verify
    assert len(result) > 0
    assert all("action" in r for r in result)
```

## Documentation Guidelines

### Docstrings

Use Google-style docstrings:

```python
def process_frame(
    frame: np.ndarray,
    config: Dict[str, Any]
) -> ProcessedFrame:
    """
    Process a game frame through the perception pipeline.
    
    This function performs object detection, OCR, and state extraction
    on a single frame.
    
    Args:
        frame: RGB image array of shape (H, W, 3)
        config: Configuration dictionary with keys:
            - conf_threshold: Detection confidence threshold
            - ocr_enabled: Whether to run OCR
            
    Returns:
        ProcessedFrame object containing:
            - detections: List of detected objects
            - state: Extracted game state
            - metadata: Processing metadata
            
    Raises:
        ValueError: If frame is not 3-channel RGB
        RuntimeError: If detection fails
        
    Example:
        >>> frame = capture_screen()
        >>> config = {"conf_threshold": 0.5, "ocr_enabled": True}
        >>> result = process_frame(frame, config)
        >>> print(result.state)
    """
    pass
```

### Markdown Files

- Use clear headings
- Include code examples
- Add screenshots where helpful
- Keep line length under 100 characters

## Security Guidelines

### Input Validation

Always validate user input:

```python
def set_confidence(threshold: float) -> None:
    """Set detection confidence threshold."""
    if not 0.0 <= threshold <= 1.0:
        raise ValueError(f"Threshold must be in [0, 1], got {threshold}")
    self.threshold = threshold
```

### Sensitive Data

Never commit:
- API keys
- Passwords
- Personal data
- Trained model weights (use Git LFS or external storage)

## Release Process

Releases are managed by maintainers:

1. Update version in `pyproject.toml` and `gamepilot/__init__.py`
2. Update `CHANGELOG.md`
3. Create release branch: `release/v0.X.0`
4. Tag release: `git tag v0.X.0`
5. Push to GitHub
6. CI builds and publishes

## Getting Help

- **Questions:** Open a GitHub Discussion
- **Bugs:** Open a GitHub Issue with `bug` label
- **Features:** Open a GitHub Issue with `enhancement` label
- **Security:** Email security@gamepilot.ai (private)

## Recognition

Contributors are recognized in:
- README.md Contributors section
- CHANGELOG.md for significant contributions
- Release notes

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to GamePilot!** 🚀
