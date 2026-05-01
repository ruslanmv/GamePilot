#!/usr/bin/env python3
"""
GamePilot Autopilot - Real-World Usage Examples
Demonstrates the exact scenarios requested by the user
"""

print("=" * 80)
print("GamePilot Autopilot Mode - Usage Examples")
print("=" * 80)

# Example 1: STUCK ON MISSION
print("\n📍 Example 1: Stuck on Boss Fight")
print("-" * 80)
print("""
Scenario: You've died 20 times to the same boss and need help.

Code:
""")

print('''
from gamepilot.autopilot import AutopilotController, AutopilotMode
from gamepilot.environments import PrivateSandbox

# Setup
env = PrivateSandbox("elden_ring_offline")
autopilot = AutopilotController(env)

# Let AI attempt the boss for 15 minutes
session = autopilot.start_autopilot(
    mode=AutopilotMode.COMPLETE_MISSION,
    goal_description="Defeat the boss",
    duration_seconds=900,  # 15 minutes
    goal_params={"boss_name": "Malenia", "strategy": "defensive"}
)

print("AI is attempting boss fight...")
print("Watch and learn the patterns!")

# Monitor progress
import time
while autopilot.is_running:
    status = autopilot.get_status()
    print(f"⏱️  Time remaining: {status['time_remaining']:.0f}s")
    print(f"⚔️  Actions taken: {status['actions_count']}")
    time.sleep(5)

# Results
if session.success:
    print("✅ Boss defeated! You can continue now.")
else:
    print("⚠️  AI tried but didn't succeed. You learned some strategies though!")

print(f"Total actions attempted: {len(session.actions_taken)}")
''')

# Example 2: NEED HELP BUILDING
print("\n📍 Example 2: Help Me Build Something")
print("-" * 80)
print("""
Scenario: You want a castle but don't know how to build it.

Code:
""")

print('''
from gamepilot.autopilot import AutopilotController, AutopilotMode
from gamepilot.app.domains.construction import ConstructionPlanner
from gamepilot.environments import PrivateSandbox

# Get construction plan
planner = ConstructionPlanner()
plan = planner.plan("castle", material="stone")

print(f"Castle plan:")
print(f"  - Steps: {len(plan.steps)}")
print(f"  - Resources needed: {plan.total_resources}")
print(f"  - Estimated time: {plan.estimated_time_minutes} min")

# Let AI build it
env = PrivateSandbox("minecraft_creative")
autopilot = AutopilotController(env)

session = autopilot.start_autopilot(
    mode=AutopilotMode.BUILD_STRUCTURE,
    goal_description="Build a stone castle",
    duration_seconds=3600,  # 1 hour
    goal_params={
        "construction_plan": plan,
        "location": (100, 64, 100)
    }
)

print("🏗️  AI is building your castle...")
print("Watch to learn building techniques!")

while autopilot.is_running:
    status = autopilot.get_status()
    print(f"Building... {status['completion']:.1f}% complete")
    time.sleep(10)

print("✅ Castle complete! Enjoy your new base!")
''')

# Example 3: AFK BREAK
print("\n📍 Example 3: AFK Break (Going to Eat)")
print("-" * 80)
print("""
Scenario: You need 10 minutes to eat but don't want to log out.

Code:
""")

print('''
from gamepilot.autopilot import AutopilotController, AutopilotMode, SAFE_AFK_CONFIG
from gamepilot.environments import PrivateSandbox

env = PrivateSandbox("your_game")
autopilot = AutopilotController(env)

# Safe AFK mode - AI just keeps you alive
session = autopilot.start_autopilot(
    mode=AutopilotMode.STAY_ALIVE,
    goal_description="Keep safe while I eat",
    duration_seconds=600,  # Exactly 10 minutes
    goal_params={
        "safety_priority": "maximum",
        "avoid_combat": True,
        "find_safe_spot": True
    }
)

print("🍕 Going to eat! AI will keep you safe for 10 minutes.")
print("✋ Press Ctrl+C for emergency stop if needed.")

# What AI does:
# 1. Finds safe hiding spot
# 2. If enemy approaches → hide/run
# 3. No fighting, just survival
# 4. After 10 min → returns control automatically

import time
try:
    while autopilot.is_running:
        status = autopilot.get_status()
        mins_left = status['time_remaining'] / 60
        print(f"⏰ {mins_left:.1f} minutes until you're back", end='\\r')
        time.sleep(5)
except KeyboardInterrupt:
    autopilot.emergency_stop()
    print("\\n🛑 Emergency stop activated!")

print("\\n✅ Welcome back! Character is safe.")
print(f"AI took {len(session.actions_taken)} defensive actions to keep you alive.")
''')

# Example 4: RESOURCE GATHERING
print("\n📍 Example 4: Gather Resources While AFK")
print("-" * 80)
print("""
Scenario: You need 1000 wood but don't want to grind.

Code:
""")

print('''
from gamepilot.autopilot import AutopilotController, AutopilotMode

env = PrivateSandbox("game")
autopilot = AutopilotController(env)

session = autopilot.start_autopilot(
    mode=AutopilotMode.GATHER_RESOURCES,
    goal_description="Gather 1000 wood",
    duration_seconds=1800,  # 30 min max
    goal_params={
        "resource_type": "wood",
        "target_quantity": 1000,
        "auto_return_when_full": True  # Return to storage automatically
    }
)

print("⛏️  AI is gathering wood for you...")
print("You can go do something else!")

while autopilot.is_running:
    status = autopilot.get_status()
    # In production, would show actual resource count
    print(f"Gathering resources... {status['actions_count']} actions taken", end='\\r')
    time.sleep(5)

print("\\n✅ Resource gathering complete!")
print(f"Session duration: {session.get_elapsed_seconds():.0f} seconds")
''')

# Example 5: QUICK DEMO
print("\n📍 Example 5: Quick Demo (Simplest Usage)")
print("-" * 80)
print("""
Scenario: Just want AI to help for 5 minutes.

Code:
""")

print('''
from gamepilot.autopilot import AutopilotController, AutopilotMode
from gamepilot.environments import PrivateSandbox

# One-liner setup
env = PrivateSandbox("my_game")
autopilot = AutopilotController(env)

# Start autopilot with minimal config
session = autopilot.start_autopilot(
    mode=AutopilotMode.STAY_ALIVE,  # Safest mode
    goal_description="Help me for 5 minutes",
    duration_seconds=300  # 5 minutes
)

print("🤖 AI is helping for 5 minutes...")

# Wait for completion
import time
time.sleep(300)  # Or do other things

print("✅ Done! Control returned.")
''')

# Safety reminder
print("\n" + "=" * 80)
print("⚠️  IMPORTANT SAFETY NOTES")
print("=" * 80)
print("""
Autopilot Mode Safety Features:

✅ Time-limited (you choose duration)
✅ Offline games only (multiplayer blocked)
✅ Emergency stop (Ctrl+C or API)
✅ Full action logging
✅ Auto-stop on danger (low health, etc.)
✅ Rate limiting (no spam)
✅ Returns control smoothly

Recommended Settings:
- Start with short durations (5-10 min)
- Use SAFE_AFK_CONFIG for AFK breaks
- Monitor first few times
- Review action logs

DO NOT use autopilot for:
❌ Competitive multiplayer
❌ MMO grinding for profit
❌ Violating game ToS
❌ Replacing actual gameplay
""")

print("\n" + "=" * 80)
print("Ready to try Autopilot Mode? 🚀")
print("=" * 80)
print("""
Installation:
    pip install gamepilot[autopilot]

Quick start:
    python examples/autopilot_examples.py

Documentation:
    docs/AUTOPILOT_GUIDE.md

Questions? Check the guide or open an issue on GitHub!
""")
