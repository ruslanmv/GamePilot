"""
GamePilot Companion - LLM Integration
Supports OpenAI, IBM watsonx, and Anthropic Claude
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import os

# Optional imports - fail gracefully if not installed
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from ibm_watsonx_ai.foundation_models import Model
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
    WATSONX_AVAILABLE = True
except ImportError:
    WATSONX_AVAILABLE = False

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    WATSONX = "watsonx"
    ANTHROPIC = "anthropic"
    MOCK = "mock"


class GamePilotCompanion:
    """
    AI companion that provides strategic advice using LLMs.
    
    Supports multiple providers:
    - OpenAI (GPT-4, GPT-3.5-turbo)
    - IBM watsonx (Llama, Mixtral, etc.)
    - Anthropic Claude
    - Mock (for testing without API keys)
    """
    
    SYSTEM_PROMPT = """You are GamePilot, an AI companion for gamers.

Your role:
- Analyze game state and provide strategic advice
- Help with planning (building, combat, exploration, resource management)
- Warn about dangers and suggest safety measures
- Provide step-by-step guidance
- Suggest optimizations and efficiency improvements

Your personality:
- Concise and action-oriented
- Supportive and encouraging
- Strategic thinker
- Safety-conscious

Your limits:
- Never encourage cheating or ToS violations
- Focus on single-player or sandbox games
- Prioritize user safety and enjoyment
- Respect game balance and intended mechanics

Response format:
- Be direct and specific
- Use bullet points for multiple suggestions
- Include reasoning when helpful
- Keep responses under 200 words unless asked for detail"""

    def __init__(
        self,
        provider: LLMProvider = LLMProvider.OPENAI,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the companion.
        
        Args:
            provider: LLM provider to use
            api_key: API key (reads from env if not provided)
            model: Model name (uses provider default if not specified)
            **kwargs: Provider-specific configuration
        """
        self.provider = provider
        self.conversation_history: List[Dict[str, str]] = []
        
        # Initialize based on provider
        if provider == LLMProvider.OPENAI:
            self._init_openai(api_key, model)
        elif provider == LLMProvider.WATSONX:
            self._init_watsonx(api_key, model, **kwargs)
        elif provider == LLMProvider.ANTHROPIC:
            self._init_anthropic(api_key, model)
        elif provider == LLMProvider.MOCK:
            self._init_mock()
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def _init_openai(self, api_key: Optional[str], model: Optional[str]):
        """Initialize OpenAI client."""
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package not installed. Install with: pip install openai")
        
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model or "gpt-4"
    
    def _init_watsonx(self, api_key: Optional[str], model: Optional[str], **kwargs):
        """Initialize IBM watsonx client."""
        if not WATSONX_AVAILABLE:
            raise ImportError("ibm-watsonx-ai package not installed. Install with: pip install ibm-watsonx-ai")
        
        project_id = kwargs.get("project_id") or os.getenv("WATSONX_PROJECT_ID")
        url = kwargs.get("url") or os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
        
        credentials = {
            "apikey": api_key or os.getenv("WATSONX_API_KEY"),
            "url": url
        }
        
        self.model_id = model or "meta-llama/llama-3-70b-instruct"
        self.model = Model(
            model_id=self.model_id,
            credentials=credentials,
            project_id=project_id,
            params={
                GenParams.MAX_NEW_TOKENS: 500,
                GenParams.TEMPERATURE: 0.7,
                GenParams.TOP_P: 0.9,
            }
        )
    
    def _init_anthropic(self, api_key: Optional[str], model: Optional[str]):
        """Initialize Anthropic Claude client."""
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package not installed. Install with: pip install anthropic")
        
        self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.model = model or "claude-3-5-sonnet-20241022"
    
    def _init_mock(self):
        """Initialize mock provider for testing."""
        self.model = "mock"
    
    def chat(
        self,
        user_message: str,
        game_state: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Chat with the companion about the current game situation.
        
        Args:
            user_message: What the user is asking
            game_state: Current game state from perception
            context: Additional context (inventory, objectives, etc.)
            
        Returns:
            AI companion's response
        """
        # Build state summary
        state_summary = self._build_state_summary(game_state or {}, context or {})
        
        # Build full prompt
        full_prompt = f"{state_summary}\n\nUser: {user_message}"
        
        # Get response from provider
        if self.provider == LLMProvider.OPENAI:
            response = self._chat_openai(full_prompt)
        elif self.provider == LLMProvider.WATSONX:
            response = self._chat_watsonx(full_prompt)
        elif self.provider == LLMProvider.ANTHROPIC:
            response = self._chat_anthropic(full_prompt)
        else:  # MOCK
            response = self._chat_mock(user_message, game_state)
        
        # Store in history
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user": user_message,
            "assistant": response,
            "game_state": game_state
        })
        
        return response
    
    def _build_state_summary(self, game_state: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Build a human-readable summary of the game state."""
        lines = ["Current Game State:"]
        
        # Core stats
        if "hp" in game_state:
            hp = game_state["hp"]
            hp_max = game_state.get("hp_max", 100)
            hp_pct = (hp / hp_max * 100) if hp_max > 0 else 0
            lines.append(f"- Health: {hp}/{hp_max} ({hp_pct:.0f}%)")
        
        if "mp" in game_state:
            mp = game_state["mp"]
            mp_max = game_state.get("mp_max", 100)
            lines.append(f"- Mana/Energy: {mp}/{mp_max}")
        
        # Threats
        if game_state.get("enemy_near"):
            lines.append("- ⚠️ Enemy nearby!")
        
        # Opportunities
        if game_state.get("loot_visible"):
            lines.append("- 💰 Loot available")
        
        if game_state.get("npc_visible"):
            lines.append("- 👤 NPC present")
        
        # Navigation
        if "quest_marker" in game_state and game_state["quest_marker"] != "unknown":
            lines.append(f"- 🎯 Quest marker: {game_state['quest_marker']}")
        
        # Status conditions
        if game_state.get("stuck"):
            lines.append("- ⚠️ Player appears stuck")
        
        # Context information
        if context.get("inventory"):
            inv = context["inventory"]
            lines.append(f"- Inventory: {len(inv)} items")
        
        if context.get("current_objective"):
            lines.append(f"- Objective: {context['current_objective']}")
        
        return "\n".join(lines)
    
    def _chat_openai(self, prompt: str) -> str:
        """Chat using OpenAI."""
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )
        
        return response.choices[0].message.content
    
    def _chat_watsonx(self, prompt: str) -> str:
        """Chat using IBM watsonx."""
        full_prompt = f"{self.SYSTEM_PROMPT}\n\n{prompt}\n\nAssistant:"
        
        response = self.model.generate_text(prompt=full_prompt)
        return response.strip()
    
    def _chat_anthropic(self, prompt: str) -> str:
        """Chat using Anthropic Claude."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=300,
            system=self.SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text
    
    def _chat_mock(self, user_message: str, game_state: Optional[Dict[str, Any]]) -> str:
        """Mock response for testing."""
        msg_lower = user_message.lower()
        
        if "help" in msg_lower or "what" in msg_lower:
            if game_state and game_state.get("enemy_near"):
                return "You're in danger! Enemy nearby with low health. Recommend: retreat to safe area, heal, then re-engage from better position."
            return "I can help with strategy, building, combat, and exploration. What would you like to do?"
        
        if "build" in msg_lower:
            return "Building strategy:\n1. Gather resources first\n2. Choose safe location\n3. Start with foundation\n4. Build walls before roof\n5. Add door/windows last"
        
        if "fight" in msg_lower or "combat" in msg_lower:
            if game_state and game_state.get("hp", 100) < 30:
                return "Warning: Low health! Avoid combat. Heal first or retreat."
            return "Combat tips:\n- Keep health above 50%\n- Use cover when possible\n- Save strong abilities for tough enemies\n- Retreat if overwhelmed"
        
        return "I'm here to help. Tell me what you're trying to do or ask for specific advice."
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history."""
        return self.conversation_history[-limit:]
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()


def create_companion(
    provider: str = "openai",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
) -> GamePilotCompanion:
    """
    Factory function to create a companion.
    
    Args:
        provider: "openai", "watsonx", "anthropic", or "mock"
        api_key: API key (optional, reads from env)
        model: Model name (optional, uses default)
        **kwargs: Provider-specific config
        
    Returns:
        Configured GamePilotCompanion
    
    Example:
        # OpenAI
        companion = create_companion("openai", model="gpt-4")
        
        # watsonx
        companion = create_companion(
            "watsonx",
            model="meta-llama/llama-3-70b-instruct",
            project_id="your-project-id"
        )
        
        # Mock (no API key needed)
        companion = create_companion("mock")
    """
    provider_enum = LLMProvider(provider.lower())
    return GamePilotCompanion(
        provider=provider_enum,
        api_key=api_key,
        model=model,
        **kwargs
    )


if __name__ == "__main__":
    # Test with mock provider
    print("Testing GamePilot Companion (Mock Mode)\n")
    
    companion = create_companion("mock")
    
    # Test 1: General help
    response = companion.chat(
        "What should I do?",
        game_state={"hp": 100, "enemy_near": False, "loot_visible": False}
    )
    print(f"Q: What should I do?")
    print(f"A: {response}\n")
    
    # Test 2: Low health combat
    response = companion.chat(
        "Should I fight this enemy?",
        game_state={"hp": 25, "enemy_near": True}
    )
    print(f"Q: Should I fight this enemy? (HP: 25)")
    print(f"A: {response}\n")
    
    # Test 3: Building
    response = companion.chat(
        "How do I build a house?",
        game_state={"hp": 100}
    )
    print(f"Q: How do I build a house?")
    print(f"A: {response}\n")
    
    print("Mock test complete!")
