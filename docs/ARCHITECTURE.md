# GamePilot Architecture

## Overview

GamePilot uses a **domain-first, universal architecture** that works across any virtual environment.

```
┌─────────────────────────────────────────────────┐
│              Application Layer                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │Companion │  │ Planning │  │ Analysis │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────┐
│               Safety Layer                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │Guardrails│  │Permission│  │RateLimit │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────┐
│            Environment Layer                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ Screen   │  │  Video   │  │Companion │      │
│  │Observer  │  │ Observer │  │   Only   │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────┐
│               Core Models                        │
│  Observation → Action → WorldState → Memory     │
└─────────────────────────────────────────────────┘
```

## Core Principles

1. **Universal Models**: Work across any game/simulation
2. **Domain-First**: Knowledge organized by domain, not game
3. **Safety-First**: Ethics and safety deeply integrated
4. **Modular**: Install only what you need
5. **Extensible**: Easy to add new features

## Module Details

### Core (`gamepilot/core/`)

Universal data structures:
- **Observation**: What AI sees (visual, text, structured data)
- **Action**: What AI can do (keyboard, mouse, abstract)
- **WorldState**: Current environment state
- **Events & Goals**: What happens and what to achieve
- **Memory**: Experience storage and learning

### Environments (`gamepilot/environments/`)

Abstraction layer for any interactive world:
- **BaseEnvironment**: Interface all environments implement
- **ScreenObserver**: Real-time game observation
- **VideoObserver**: Recorded gameplay analysis
- **CompanionOnly**: Chat without visual input (safest)
- **PrivateSandbox**: Safe automated testing

### Safety (`gamepilot/safety/`)

Ethics and safety enforcement:
- **Guardrails**: Rule-based safety checks
- **Permissions**: What AI is allowed to do
- **RateLimiter**: Prevents excessive actions

### Companion (`gamepilot/app/companion/`)

AI chat assistant:
- **LLM Chat**: Multi-provider support
- **Intent Parser**: Natural language understanding

### Domains (`gamepilot/app/domains/`)

Specialized knowledge modules:
- **Construction**: Building and planning
- **Combat**: (Coming v0.4.0)
- **Exploration**: (Coming v0.4.0)

## Data Flow

```
User Input
    ↓
Environment.observe()
    ↓
Observation → WorldState
    ↓
Safety.check()
    ↓
Companion.chat() OR Planner.plan()
    ↓
Action (advice or automated)
    ↓
Memory.remember()
```

## Extension Points

Add new capabilities by:
1. Creating new Environment subclasses
2. Adding domain modules
3. Contributing domain profiles
4. Building plugins (v1.0.0)

See CONTRIBUTING.md for details.
