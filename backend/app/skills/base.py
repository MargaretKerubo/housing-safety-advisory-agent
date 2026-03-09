from abc import ABC, abstractmethod
from typing import Dict, Any, List, Callable
import json


class Skill(ABC):
    """Base class for all agent skills."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Skill name for function calling."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the skill does."""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """JSON schema for skill parameters."""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the skill with given parameters."""
        pass
    
    def to_function_schema(self) -> Dict[str, Any]:
        """Convert skill to OpenAI/Gemini function schema."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }


class SkillRegistry:
    """Registry for managing available skills."""
    
    def __init__(self):
        self._skills: Dict[str, Skill] = {}
    
    def register(self, skill: Skill):
        """Register a skill."""
        self._skills[skill.name] = skill
    
    def get(self, name: str) -> Skill:
        """Get a skill by name."""
        return self._skills.get(name)
    
    def list_schemas(self) -> List[Dict[str, Any]]:
        """Get all skill schemas for function calling."""
        return [skill.to_function_schema() for skill in self._skills.values()]
    
    def execute(self, name: str, **kwargs) -> Dict[str, Any]:
        """Execute a skill by name."""
        skill = self.get(name)
        if not skill:
            return {"error": f"Skill '{name}' not found"}
        return skill.execute(**kwargs)
