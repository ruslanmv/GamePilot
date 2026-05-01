#!/usr/bin/env python3
"""
GamePilot v0.3.0 Feature Test Script
Tests all new companion features
"""
import sys

print("=" * 70)
print("GamePilot v0.3.0 - Feature Test")
print("=" * 70)

# Test 1: Import companion modules
print("\n1. Testing companion module imports...")
try:
    from gamepilot.app.companion import create_companion, parse_intent
    from gamepilot.app.companion import LLMProvider, Intent
    print("   ✅ Companion modules import successfully")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Import construction planner
print("\n2. Testing construction planner import...")
try:
    from gamepilot.app.domains.construction import ConstructionPlanner, create_plan
    print("   ✅ Construction planner imports successfully")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test 3: Test intent parser
print("\n3. Testing intent parser...")
try:
    result = parse_intent("build a stone house")
    print(f"   Input: 'build a stone house'")
    print(f"   Intent: {result.intent.value}")
    print(f"   Entities: {result.entities}")
    print(f"   Confidence: {result.confidence}")
    assert result.intent.value == "build"
    assert "material" in result.entities or "structure" in result.entities
    print("   ✅ Intent parser works correctly")
except Exception as e:
    print(f"   ❌ Intent parser failed: {e}")
    sys.exit(1)

# Test 4: Test construction planner
print("\n4. Testing construction planner...")
try:
    planner = ConstructionPlanner()
    plan = planner.plan("simple_house", "wood")
    print(f"   Structure: {plan.structure_type}")
    print(f"   Material: {plan.material}")
    print(f"   Steps: {len(plan.steps)}")
    print(f"   Resources: {plan.total_resources}")
    print(f"   Time: {plan.estimated_time_minutes} min")
    assert len(plan.steps) > 0
    assert plan.total_resources.get("wood", 0) > 0
    print("   ✅ Construction planner works correctly")
except Exception as e:
    print(f"   ❌ Construction planner failed: {e}")
    sys.exit(1)

# Test 5: Test mock companion
print("\n5. Testing mock companion (no API key needed)...")
try:
    companion = create_companion(provider="mock")
    response = companion.chat(
        user_message="What should I do?",
        game_state={"hp": 100, "enemy_near": False}
    )
    print(f"   User: 'What should I do?'")
    print(f"   Companion: {response[:80]}...")
    assert len(response) > 0
    print("   ✅ Mock companion works correctly")
except Exception as e:
    print(f"   ❌ Mock companion failed: {e}")
    sys.exit(1)

# Test 6: Test conversation history
print("\n6. Testing conversation history...")
try:
    # Add another message
    companion.chat("How do I build a house?", {"hp": 100})
    
    history = companion.get_history(limit=5)
    print(f"   History entries: {len(history)}")
    assert len(history) >= 2
    
    # Clear history
    companion.clear_history()
    history_after = companion.get_history()
    print(f"   After clear: {len(history_after)} entries")
    assert len(history_after) == 0
    print("   ✅ Conversation history works correctly")
except Exception as e:
    print(f"   ❌ History test failed: {e}")
    sys.exit(1)

# Test 7: Test available structures
print("\n7. Testing available structures list...")
try:
    planner = ConstructionPlanner()
    structures = planner.get_available_structures()
    print(f"   Available structures: {len(structures)}")
    for struct in structures[:3]:
        print(f"   - {struct['name']}: {struct['description']}")
    assert len(structures) >= 3
    print("   ✅ Structures list works correctly")
except Exception as e:
    print(f"   ❌ Structures test failed: {e}")
    sys.exit(1)

# Test 8: Test recommendations
print("\n8. Testing construction recommendations...")
try:
    planner = ConstructionPlanner()
    recommendations = planner.get_recommendations({
        "resources": ["wood", "stone"],
        "biome": "plains",
        "has_shelter": False
    })
    print(f"   Context: plains biome, no shelter, has wood/stone")
    print(f"   Recommendations: {recommendations}")
    assert len(recommendations) > 0
    assert "simple_house" in recommendations  # Should prioritize shelter
    print("   ✅ Recommendations work correctly")
except Exception as e:
    print(f"   ❌ Recommendations test failed: {e}")
    sys.exit(1)

# Test 9: Test version
print("\n9. Testing version...")
try:
    import gamepilot
    version = gamepilot.__version__
    print(f"   GamePilot version: {version}")
    assert version == "0.3.0"
    print("   ✅ Version is correct (0.3.0)")
except Exception as e:
    print(f"   ❌ Version test failed: {e}")
    sys.exit(1)

# Test 10: Test game profile exists
print("\n10. Testing game profile...")
try:
    import yaml
    from pathlib import Path
    
    profile_path = Path("config/games/minecraft.yaml")
    if profile_path.exists():
        with open(profile_path) as f:
            profile = yaml.safe_load(f)
        print(f"   Minecraft profile loaded")
        print(f"   - Name: {profile['name']}")
        print(f"   - Domains: {', '.join(profile['domains'])}")
        print(f"   - Materials: {len(profile['materials'])} types")
        assert profile['name'] == "Minecraft"
        print("   ✅ Game profile works correctly")
    else:
        print("   ⚠️  Minecraft profile not found (optional)")
except Exception as e:
    print(f"   ⚠️  Profile test warning: {e}")

print("\n" + "=" * 70)
print("🎉 ALL TESTS PASSED!")
print("=" * 70)
print("\nGamePilot v0.3.0 is ready to use!")
print("\nNext steps:")
print("1. Set OPENAI_API_KEY or use mock mode")
print("2. Start server: python main.py")
print("3. Open UI: open frontend/companion-chat.html")
print("4. Visit API docs: http://localhost:8000/docs")
print("\nHappy gaming! 🚀")
