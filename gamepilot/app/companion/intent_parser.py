"""
Intent Parser - Natural Language Understanding for GamePilot
Extracts user intent and entities from natural language commands
"""
from typing import Tuple, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import re


class Intent(Enum):
    """Supported user intents."""
    BUILD = "build"
    COMBAT = "combat"
    EXPLORE = "explore"
    NAVIGATE = "navigate"
    HEAL = "heal"
    GATHER = "gather"
    CRAFT = "craft"
    TRADE = "trade"
    HELP = "help"
    STATUS = "status"
    UNKNOWN = "unknown"


@dataclass
class ParsedIntent:
    """Result of intent parsing."""
    intent: Intent
    confidence: float
    entities: Dict[str, any]
    raw_text: str


class IntentParser:
    """
    Parse natural language into structured intents and entities.
    
    Examples:
        "build a stone house" → BUILD intent, {material: stone, object: house}
        "fight the dragon" → COMBAT intent, {target: dragon}
        "find iron ore" → GATHER intent, {resource: iron ore}
    """
    
    # Intent patterns (regex)
    INTENT_PATTERNS = {
        Intent.BUILD: [
            r"\b(build|construct|create|make)\b.*\b(house|structure|base|shelter|tower|wall|fence|door)\b",
            r"\b(place|put)\b.*\b(block|blocks)\b",
        ],
        Intent.COMBAT: [
            r"\b(fight|attack|kill|slay|defeat|battle)\b",
            r"\b(defend|protect)\b.*\b(from|against)\b",
        ],
        Intent.EXPLORE: [
            r"\b(explore|search|scout|investigate|look\s+around)\b",
            r"\b(find|locate|discover)\b.*\b(area|zone|region|place)\b",
        ],
        Intent.NAVIGATE: [
            r"\b(go\s+to|move\s+to|travel\s+to|head\s+to|walk\s+to)\b",
            r"\b(navigate|path)\b",
        ],
        Intent.HEAL: [
            r"\b(heal|restore|recover|rest|regenerate)\b",
            r"\b(use|consume|eat|drink)\b.*\b(potion|food|medicine)\b",
        ],
        Intent.GATHER: [
            r"\b(gather|collect|harvest|mine|chop|farm)\b",
            r"\b(find|get|obtain)\b.*\b(wood|stone|ore|iron|gold|resources|materials)\b",
        ],
        Intent.CRAFT: [
            r"\b(craft|make|create|forge|brew)\b.*\b(item|tool|weapon|armor|potion)\b",
        ],
        Intent.TRADE: [
            r"\b(trade|buy|sell|purchase)\b",
            r"\b(shop|merchant|vendor)\b",
        ],
        Intent.HELP: [
            r"\b(help|assist|guide|teach|show)\b",
            r"\b(how\s+do|how\s+to|what\s+should)\b",
        ],
        Intent.STATUS: [
            r"\b(status|check|info|stats|inventory)\b",
            r"\b(what.*my|show.*my|tell.*my)\b",
        ],
    }
    
    # Entity extraction patterns
    ENTITY_PATTERNS = {
        # Materials
        "material": r"\b(wood|wooden|stone|iron|gold|diamond|steel|bronze|copper|silver|dirt|sand|glass|brick)\b",
        
        # Objects/Structures
        "structure": r"\b(house|base|shelter|tower|wall|fence|door|window|roof|floor|ceiling|bridge|castle|fort)\b",
        
        # Enemies/Targets
        "enemy": r"\b(zombie|skeleton|creeper|spider|dragon|boss|enemy|mob|monster|hostile)\b",
        
        # Resources
        "resource": r"\b(wood|lumber|stone|rock|ore|iron|gold|coal|diamond|emerald|food|meat|wheat)\b",
        
        # Directions
        "direction": r"\b(north|south|east|west|up|down|left|right|forward|backward)\b",
        
        # Quantities
        "quantity": r"\b(\d+|one|two|three|four|five|ten|twenty|fifty|hundred)\b",
        
        # Locations
        "location": r"\b(spawn|home|village|cave|mine|forest|mountain|desert|ocean|river)\b",
    }
    
    # Quantity word to number mapping
    QUANTITY_MAP = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "ten": 10, "twenty": 20, "thirty": 30, "fifty": 50, "hundred": 100
    }
    
    def parse(self, text: str) -> ParsedIntent:
        """
        Parse user input into intent and entities.
        
        Args:
            text: User's natural language input
            
        Returns:
            ParsedIntent with intent, confidence, and extracted entities
        """
        text_lower = text.lower().strip()
        
        # Match intent
        intent, confidence = self._match_intent(text_lower)
        
        # Extract entities
        entities = self._extract_entities(text_lower, intent)
        
        return ParsedIntent(
            intent=intent,
            confidence=confidence,
            entities=entities,
            raw_text=text
        )
    
    def _match_intent(self, text: str) -> Tuple[Intent, float]:
        """
        Match text against intent patterns.
        
        Returns:
            (Intent, confidence_score)
        """
        matches = []
        
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    matches.append(intent)
                    break
        
        if not matches:
            return Intent.UNKNOWN, 0.0
        
        # If multiple matches, prioritize specific intents
        if len(matches) > 1:
            # Priority order
            priority = [Intent.COMBAT, Intent.BUILD, Intent.CRAFT, Intent.GATHER, 
                       Intent.NAVIGATE, Intent.EXPLORE, Intent.HEAL]
            for intent in priority:
                if intent in matches:
                    return intent, 0.7  # Lower confidence for ambiguous
            return matches[0], 0.5
        
        return matches[0], 0.95
    
    def _extract_entities(self, text: str, intent: Intent) -> Dict[str, any]:
        """
        Extract relevant entities based on intent.
        
        Args:
            text: Normalized text
            intent: Matched intent
            
        Returns:
            Dictionary of entity_type: value
        """
        entities = {}
        
        # Extract all possible entities
        for entity_type, pattern in self.ENTITY_PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                if entity_type == "quantity":
                    # Convert to number
                    val = matches[0]
                    entities[entity_type] = self.QUANTITY_MAP.get(val, int(val) if val.isdigit() else 1)
                else:
                    entities[entity_type] = matches[0]
        
        # Intent-specific entity extraction
        if intent == Intent.BUILD:
            entities = self._extract_build_entities(text, entities)
        elif intent == Intent.COMBAT:
            entities = self._extract_combat_entities(text, entities)
        elif intent == Intent.NAVIGATE:
            entities = self._extract_navigate_entities(text, entities)
        
        return entities
    
    def _extract_build_entities(self, text: str, entities: Dict) -> Dict:
        """Extract building-specific entities."""
        # Determine what to build
        if "structure" not in entities:
            # Try to infer from context
            if "house" in text:
                entities["structure"] = "house"
            elif "tower" in text:
                entities["structure"] = "tower"
            elif "wall" in text:
                entities["structure"] = "wall"
        
        # Size indicators
        if "big" in text or "large" in text:
            entities["size"] = "large"
        elif "small" in text or "tiny" in text:
            entities["size"] = "small"
        
        return entities
    
    def _extract_combat_entities(self, text: str, entities: Dict) -> Dict:
        """Extract combat-specific entities."""
        # Combat mode
        if "defend" in text or "protect" in text:
            entities["mode"] = "defensive"
        elif "attack" in text or "fight" in text:
            entities["mode"] = "offensive"
        
        return entities
    
    def _extract_navigate_entities(self, text: str, entities: Dict) -> Dict:
        """Extract navigation-specific entities."""
        # Extract destination after "to"
        to_match = re.search(r"to\s+(?:the\s+)?(\w+(?:\s+\w+)?)", text)
        if to_match:
            entities["destination"] = to_match.group(1)
        
        return entities
    
    def get_action_parameters(self, parsed: ParsedIntent) -> Dict[str, any]:
        """
        Convert parsed intent into action parameters.
        
        Args:
            parsed: ParsedIntent result
            
        Returns:
            Dictionary of parameters for action execution
        """
        params = {
            "intent": parsed.intent.value,
            "confidence": parsed.confidence,
        }
        
        if parsed.intent == Intent.BUILD:
            params.update({
                "action": "construct",
                "object": parsed.entities.get("structure", "structure"),
                "material": parsed.entities.get("material", "wood"),
                "quantity": parsed.entities.get("quantity", 1),
            })
        
        elif parsed.intent == Intent.COMBAT:
            params.update({
                "action": "engage",
                "target": parsed.entities.get("enemy", "enemy"),
                "mode": parsed.entities.get("mode", "offensive"),
            })
        
        elif parsed.intent == Intent.NAVIGATE:
            params.update({
                "action": "move",
                "destination": parsed.entities.get("destination") or parsed.entities.get("location", "unknown"),
                "direction": parsed.entities.get("direction"),
            })
        
        elif parsed.intent == Intent.GATHER:
            params.update({
                "action": "collect",
                "resource": parsed.entities.get("resource", "resources"),
                "quantity": parsed.entities.get("quantity", 10),
            })
        
        return params


# Convenience function
def parse_intent(text: str) -> ParsedIntent:
    """Quick parse function."""
    parser = IntentParser()
    return parser.parse(text)


if __name__ == "__main__":
    # Test the intent parser
    parser = IntentParser()
    
    test_cases = [
        "build a stone house",
        "fight the dragon",
        "find iron ore in the mountain",
        "go to the village",
        "I need to heal",
        "craft a sword",
        "explore the cave",
        "gather 10 wood",
        "help me",
        "show my inventory",
    ]
    
    print("Intent Parser Test\n")
    print("=" * 70)
    
    for test in test_cases:
        result = parser.parse(test)
        params = parser.get_action_parameters(result)
        
        print(f"\nInput: '{test}'")
        print(f"Intent: {result.intent.value} (confidence: {result.confidence:.2f})")
        print(f"Entities: {result.entities}")
        print(f"Action Params: {params}")
        print("-" * 70)
