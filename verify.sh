#!/bin/bash
# GamePilot v0.1.0b1 Verification Script

echo "========================================="
echo "GamePilot v0.1.0b1 Verification"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check function
check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "${RED}✗${NC} $1"
        return 1
    fi
}

# 1. Check Python version
echo "1. Checking Python version..."
python --version | grep -E "3\.(10|11|12)" > /dev/null
check "Python 3.10-3.12"

# 2. Check gamepilot package
echo "2. Checking gamepilot package..."
python -c "import gamepilot; print(gamepilot.__version__)" 2>/dev/null | grep -F "0.1.0b1" > /dev/null
check "GamePilot v0.1.0b1 installed"

# 3. Check new perception files
echo "3. Checking new perception files..."
test -f gamepilot/app/perception/screen_capture_real.py
check "screen_capture_real.py"
test -f gamepilot/app/perception/detector_yolo.py
check "detector_yolo.py"
test -f gamepilot/app/perception/ocr_reader.py
check "ocr_reader.py"

# 4. Check new executor
echo "4. Checking new executor..."
test -f gamepilot/app/executor/input_driver.py
check "input_driver.py"

# 5. Check new model loader
echo "5. Checking model loader..."
test -f gamepilot/app/models/model_loader.py
check "model_loader.py"

# 6. Check Docker files
echo "6. Checking Docker files..."
test -f Dockerfile
check "Dockerfile"
test -f docker-compose.yml
check "docker-compose.yml"

# 7. Check CI/CD
echo "7. Checking CI/CD..."
test -f .github/workflows/ci.yml
check "CI workflow"

# 8. Check legacy removed
echo "8. Checking legacy removed..."
test ! -d legacy
check "Legacy directory removed"

# 9. Check documentation
echo "9. Checking documentation..."
test -f QUICKSTART.md
check "QUICKSTART.md"
test -f CHANGELOG.md
check "CHANGELOG.md"
test -f CONTRIBUTING.md
check "CONTRIBUTING.md"

# 10. Check imports
echo "10. Checking imports..."
python -c "from gamepilot.app.perception.screen_capture_real import ScreenCapture" 2>/dev/null
check "Import screen_capture_real"
python -c "from gamepilot.app.executor.input_driver import SafeInputDriver" 2>/dev/null
check "Import input_driver"
python -c "from gamepilot.app.models.model_loader import ModelLoader" 2>/dev/null
check "Import model_loader"

echo ""
echo "========================================="
echo "Verification Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Read QUICKSTART.md for setup guide"
echo "2. Run: gamepilot demo --video examples/sample.mp4"
echo "3. Run: gamepilot api"
echo ""
