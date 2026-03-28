"""
Workflow-aware task base class

Enables tasks to be called from LangGraph workflows and Orchestrator.
"""

from celery import Task
from typing import Optional, Dict, Any
from config import get_logger

logger = get_logger(__name__)


class WorkflowAwareTask(Task):
    """
    Base task with workflow integration
    
    Allows tasks to be called from LangGraph workflows with context.
    """
    
    def __call__(self, *args, **kwargs):
        """
        Execute task with workflow context
        
        Extracts workflow_id, workflow_state, and user_id from kwargs.
        """
        # Extract workflow context (optional)
        workflow_id = kwargs.pop('workflow_id', None)
        workflow_state = kwargs.pop('workflow_state', None)
        user_id = kwargs.pop('user_id', None)
        
        # Store in task context for access in task body
        self.workflow_id = workflow_id
        self.workflow_state = workflow_state
        self.user_id = user_id
        
        if workflow_id:
            logger.info(
                f"Task {self.name} executing in workflow context: "
                f"workflow_id={workflow_id}, user_id={user_id}"
            )
        
        try:
            # Execute the task
            result = super().__call__(*args, **kwargs)
            
            # Notify workflow of completion (if applicable)
            if workflow_id and hasattr(self, 'notify_workflow'):
                self.notify_workflow(workflow_id, result)
            
            return result
        
        except Exception as e:
            # Notify workflow of failure (if applicable)
            if workflow_id and hasattr(self, 'notify_workflow_failure'):
                self.notify_workflow_failure(workflow_id, str(e))
            raise
    
    def notify_workflow(self, workflow_id: str, result: Dict[str, Any]):
        """
        Notify LangGraph workflow of task completion
        
        This will be implemented in Этап 5 when Orchestrator is ready.
        
        Args:
            workflow_id: LangGraph workflow ID
            result: Task result
        """
        logger.info(f"Task {self.name} completed for workflow {workflow_id}")
        # TODO: Implement in Этап 5
        # orchestrator.notify_task_completion(workflow_id, self.name, result)
    
    def notify_workflow_failure(self, workflow_id: str, error: str):
        """
        Notify LangGraph workflow of task failure
        
        Args:
            workflow_id: LangGraph workflow ID
            error: Error message
        """
        logger.error(f"Task {self.name} failed for workflow {workflow_id}: {error}")
        # TODO: Implement in Этап 5
        # orchestrator.notify_task_failure(workflow_id, self.name, error)
