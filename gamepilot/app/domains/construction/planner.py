"""
Construction Planner - Domain module for building and construction tasks
Generates step-by-step building plans for various structures
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


class Material(Enum):
    """Common building materials."""
    WOOD = "wood"
    STONE = "stone"
    IRON = "iron"
    DIAMOND = "diamond"
    BRICK = "brick"
    GLASS = "glass"
    DIRT = "dirt"
    SAND = "sand"


@dataclass
class BuildingStep:
    """Single step in a construction plan."""
    phase: str
    action: str
    material: str
    quantity: int
    description: str
    coordinates: Optional[Tuple[int, int, int]] = None
    order: int = 0


@dataclass
class ConstructionPlan:
    """Complete building plan with resource requirements."""
    structure_type: str
    material: str
    steps: List[BuildingStep] = field(default_factory=list)
    total_resources: Dict[str, int] = field(default_factory=dict)
    estimated_time_minutes: int = 0
    difficulty: str = "medium"


class ConstructionPlanner:
    """
    Generates step-by-step construction plans for various structures.
    
    Supports:
    - Houses (simple, medium, large)
    - Towers (watch tower, defense tower)
    - Walls (basic, reinforced)
    - Utility structures (storage, farm, workshop)
    """
    
    # Blueprint database
    BLUEPRINTS = {
        "simple_house": {
            "description": "Basic 4x4 shelter with door",
            "difficulty": "easy",
            "time_minutes": 10,
            "phases": {
                "foundation": [
                    ("place_block", 16, "4x4 floor foundation"),
                ],
                "walls": [
                    ("place_block", 32, "4 walls, 2 blocks high"),
                ],
                "roof": [
                    ("place_block", 16, "Flat roof covering"),
                ],
                "entrance": [
                    ("place_door", 1, "Door for entrance"),
                ],
            }
        },
        
        "medium_house": {
            "description": "6x6 house with windows and interior",
            "difficulty": "medium",
            "time_minutes": 20,
            "phases": {
                "foundation": [
                    ("place_block", 36, "6x6 floor foundation"),
                ],
                "walls": [
                    ("place_block", 60, "4 walls, 3 blocks high"),
                ],
                "windows": [
                    ("place_glass", 8, "4 windows (2 per side)"),
                ],
                "roof": [
                    ("place_block", 42, "Peaked roof"),
                ],
                "interior": [
                    ("place_block", 12, "Interior walls/partitions"),
                ],
                "entrance": [
                    ("place_door", 1, "Main door"),
                ],
            }
        },
        
        "tower": {
            "description": "3x3 defensive tower, 8 blocks high",
            "difficulty": "medium",
            "time_minutes": 15,
            "phases": {
                "foundation": [
                    ("place_block", 9, "3x3 base"),
                ],
                "walls": [
                    ("place_block", 64, "3x3 hollow tower, 8 blocks high"),
                ],
                "battlements": [
                    ("place_block", 12, "Top battlements with gaps"),
                ],
                "ladder": [
                    ("place_ladder", 7, "Climbing ladder inside"),
                ],
            }
        },
        
        "wall": {
            "description": "10-block long defensive wall",
            "difficulty": "easy",
            "time_minutes": 5,
            "phases": {
                "base": [
                    ("place_block", 10, "Wall base layer"),
                ],
                "wall": [
                    ("place_block", 30, "Wall 3 blocks high"),
                ],
                "top": [
                    ("place_block", 10, "Wall top layer"),
                ],
            }
        },
        
        "farm": {
            "description": "8x8 farming area with water source",
            "difficulty": "easy",
            "time_minutes": 8,
            "phases": {
                "till": [
                    ("till_soil", 64, "Prepare farmland"),
                ],
                "water": [
                    ("place_water", 1, "Central water source"),
                ],
                "fence": [
                    ("place_fence", 32, "Perimeter fence"),
                ],
                "gate": [
                    ("place_gate", 1, "Entry gate"),
                ],
            }
        },
        
        "storage": {
            "description": "Storage room with chests",
            "difficulty": "easy",
            "time_minutes": 12,
            "phases": {
                "floor": [
                    ("place_block", 25, "5x5 floor"),
                ],
                "walls": [
                    ("place_block", 40, "Walls 2 blocks high"),
                ],
                "chests": [
                    ("place_chest", 8, "8 storage chests"),
                ],
                "roof": [
                    ("place_block", 25, "Roof covering"),
                ],
                "door": [
                    ("place_door", 1, "Entrance door"),
                ],
            }
        },
    }
    
    # Material recommendations by structure type
    MATERIAL_RECOMMENDATIONS = {
        "simple_house": ["wood", "stone"],
        "medium_house": ["wood", "stone", "brick"],
        "tower": ["stone", "brick", "iron"],
        "wall": ["stone", "brick"],
        "farm": ["wood", "dirt"],
        "storage": ["wood", "stone"],
    }
    
    def plan(
        self,
        structure_type: str,
        material: Optional[str] = None,
        size_multiplier: float = 1.0
    ) -> ConstructionPlan:
        """
        Generate a construction plan for a structure.
        
        Args:
            structure_type: Type of structure (e.g., "simple_house", "tower")
            material: Material to use (defaults to recommended)
            size_multiplier: Scale factor for structure size
            
        Returns:
            Complete ConstructionPlan
        """
        blueprint = self.BLUEPRINTS.get(structure_type)
        if not blueprint:
            return self._unknown_structure_plan(structure_type)
        
        # Select material
        if material is None:
            material = self.MATERIAL_RECOMMENDATIONS[structure_type][0]
        
        # Build plan
        plan = ConstructionPlan(
            structure_type=structure_type,
            material=material,
            difficulty=blueprint["difficulty"],
            estimated_time_minutes=int(blueprint["time_minutes"] * size_multiplier)
        )
        
        # Generate steps
        order = 1
        for phase_name, actions in blueprint["phases"].items():
            for action_type, base_qty, description in actions:
                # Scale quantity
                quantity = int(base_qty * size_multiplier)
                
                # Determine material for this step
                step_material = material
                if action_type == "place_glass":
                    step_material = "glass"
                elif action_type in ["place_door", "place_gate"]:
                    step_material = "wood"  # Doors typically wood
                elif action_type == "place_chest":
                    step_material = "wood"
                elif action_type == "place_ladder":
                    step_material = "wood"
                
                step = BuildingStep(
                    phase=phase_name,
                    action=action_type,
                    material=step_material,
                    quantity=quantity,
                    description=f"{phase_name.title()}: {description}",
                    order=order
                )
                
                plan.steps.append(step)
                order += 1
        
        # Calculate total resources
        plan.total_resources = self.calculate_resources(plan.steps)
        
        return plan
    
    def calculate_resources(self, steps: List[BuildingStep]) -> Dict[str, int]:
        """
        Calculate total resources needed for a construction plan.
        
        Args:
            steps: List of building steps
            
        Returns:
            Dictionary of {material: quantity}
        """
        resources = {}
        
        for step in steps:
            if step.material:
                resources[step.material] = resources.get(step.material, 0) + step.quantity
        
        return resources
    
    def get_available_structures(self) -> List[Dict[str, str]]:
        """
        Get list of all available structure types.
        
        Returns:
            List of structure info dictionaries
        """
        structures = []
        for name, blueprint in self.BLUEPRINTS.items():
            structures.append({
                "name": name,
                "description": blueprint["description"],
                "difficulty": blueprint["difficulty"],
                "time_estimate": f"{blueprint['time_minutes']} minutes"
            })
        return structures
    
    def estimate_build_time(self, plan: ConstructionPlan, player_skill: str = "medium") -> int:
        """
        Estimate build time based on plan and player skill.
        
        Args:
            plan: Construction plan
            player_skill: "beginner", "medium", "expert"
            
        Returns:
            Estimated time in minutes
        """
        base_time = plan.estimated_time_minutes
        
        multipliers = {
            "beginner": 1.5,
            "medium": 1.0,
            "expert": 0.7
        }
        
        return int(base_time * multipliers.get(player_skill, 1.0))
    
    def _unknown_structure_plan(self, structure_type: str) -> ConstructionPlan:
        """Generate error plan for unknown structure type."""
        plan = ConstructionPlan(
            structure_type=structure_type,
            material="unknown",
            difficulty="unknown"
        )
        
        plan.steps.append(BuildingStep(
            phase="error",
            action="error",
            material="",
            quantity=0,
            description=f"Unknown structure type: {structure_type}. Available types: {', '.join(self.BLUEPRINTS.keys())}",
            order=1
        ))
        
        return plan
    
    def get_recommendations(self, context: Dict[str, any]) -> List[str]:
        """
        Get building recommendations based on context.
        
        Args:
            context: Game context (available resources, biome, etc.)
            
        Returns:
            List of recommended structure types
        """
        recommendations = []
        
        available_resources = set(context.get("resources", []))
        biome = context.get("biome", "plains")
        has_shelter = context.get("has_shelter", False)
        
        # Priority recommendations
        if not has_shelter:
            recommendations.append("simple_house")
        
        if "stone" in available_resources:
            recommendations.append("tower")
        
        if biome in ["plains", "forest"] and len(available_resources) > 3:
            recommendations.append("farm")
        
        if has_shelter:
            recommendations.append("storage")
        
        return recommendations[:3]  # Top 3


def create_plan(structure: str, material: str = None) -> ConstructionPlan:
    """Convenience function to create a construction plan."""
    planner = ConstructionPlanner()
    return planner.plan(structure, material)


if __name__ == "__main__":
    # Test the construction planner
    planner = ConstructionPlanner()
    
    print("Construction Planner Test\n")
    print("=" * 70)
    
    # Test 1: Simple house
    plan = planner.plan("simple_house", "wood")
    print(f"\n{plan.structure_type.upper()} (Material: {plan.material})")
    print(f"Difficulty: {plan.difficulty} | Time: {plan.estimated_time_minutes} min")
    print("\nSteps:")
    for step in plan.steps:
        print(f"  {step.order}. [{step.phase}] {step.description}")
        print(f"     Action: {step.action}, Material: {step.material}, Qty: {step.quantity}")
    
    print(f"\nTotal Resources Needed:")
    for material, qty in plan.total_resources.items():
        print(f"  - {material}: {qty}")
    
    print("\n" + "=" * 70)
    
    # Test 2: Tower
    plan = planner.plan("tower", "stone")
    print(f"\n{plan.structure_type.upper()} (Material: {plan.material})")
    print(f"Total Resources: {plan.total_resources}")
    
    print("\n" + "=" * 70)
    
    # Test 3: List available structures
    print("\nAvailable Structures:")
    for struct in planner.get_available_structures():
        print(f"  - {struct['name']}: {struct['description']}")
        print(f"    Difficulty: {struct['difficulty']}, Time: {struct['time_estimate']}")
