"""
Base Workflow

Abstract base class for all workflows in the system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from config import get_logger

logger = get_logger(__name__)


class BaseWorkflow(ABC):
    """
    Abstract base class for workflows
    
    All workflows must inherit from this class and implement run() method.
    """
    
    def __init__(self):
        self.logger = logger
    
    @abstractmethod
    async def run(
        self,
        context: Dict[str, Any],
        workflow_id: str,
        user_id: Optional[int] = None,
        shop_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute the workflow
        
        Args:
            context: Input context/data for workflow
            workflow_id: Unique workflow execution ID
            user_id: Optional user ID
            shop_id: Optional shop ID
            
        Returns:
            Workflow execution result
        """
        pass
    
    def log_step(self, step_name: str, data: Any = None):
        """Log workflow step"""
        self.logger.info(f"Workflow step: {step_name}, data: {data}")
