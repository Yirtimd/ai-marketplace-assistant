"""
Workflow Registry

Central registry for all available workflows in the system.
"""

from typing import Dict, Type, Optional, Callable
from config import get_logger

logger = get_logger(__name__)


class WorkflowRegistry:
    """
    Registry for managing available workflows
    
    Follows the Factory Pattern to create workflow instances.
    """
    
    def __init__(self):
        self._workflows: Dict[str, Type] = {}
        self._workflow_metadata: Dict[str, dict] = {}
        logger.info("WorkflowRegistry initialized")
    
    def register(
        self,
        name: str,
        workflow_class: Type,
        description: str = "",
        category: str = "general"
    ):
        """
        Register a workflow
        
        Args:
            name: Unique workflow name
            workflow_class: Workflow class
            description: Human-readable description
            category: Workflow category (analytics, inventory, content, etc.)
        """
        if name in self._workflows:
            logger.warning(f"Workflow '{name}' already registered, overwriting")
        
        self._workflows[name] = workflow_class
        self._workflow_metadata[name] = {
            "description": description,
            "category": category,
            "class": workflow_class.__name__
        }
        
        logger.info(f"Registered workflow: {name} ({category})")
    
    def get(self, name: str) -> Optional[Type]:
        """
        Get workflow class by name
        
        Args:
            name: Workflow name
            
        Returns:
            Workflow class or None
        """
        workflow_class = self._workflows.get(name)
        
        if not workflow_class:
            logger.error(f"Workflow '{name}' not found in registry")
            return None
        
        return workflow_class
    
    def create(self, name: str, **kwargs):
        """
        Create workflow instance
        
        Args:
            name: Workflow name
            **kwargs: Workflow initialization parameters
            
        Returns:
            Workflow instance
        """
        workflow_class = self.get(name)
        
        if not workflow_class:
            raise ValueError(f"Workflow '{name}' not registered")
        
        logger.info(f"Creating workflow instance: {name}")
        return workflow_class(**kwargs)
    
    def list_workflows(self, category: Optional[str] = None) -> Dict[str, dict]:
        """
        List all registered workflows
        
        Args:
            category: Optional filter by category
            
        Returns:
            Dictionary of workflows with metadata
        """
        if category:
            return {
                name: meta
                for name, meta in self._workflow_metadata.items()
                if meta["category"] == category
            }
        return self._workflow_metadata.copy()
    
    def exists(self, name: str) -> bool:
        """Check if workflow exists"""
        return name in self._workflows


# Global registry instance
workflow_registry = WorkflowRegistry()
