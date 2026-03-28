"""
Orchestrator

Central component for managing and executing AI workflows.

Responsibilities:
- Accept requests (from API, Events, Tasks)
- Determine appropriate workflow
- Execute workflow
- Track workflow state
- Notify completion
"""

from typing import Dict, Any, Optional
from datetime import datetime
from uuid import uuid4

from config import get_logger
from database import db_manager
from database.repositories import shop_repository
from database.models.workflow_state import WorkflowStatus
from orchestrator.registry import workflow_registry

logger = get_logger(__name__)


class Orchestrator:
    """
    Central orchestrator for AI workflows
    
    Follows the Orchestration Pattern to coordinate complex AI processes.
    """
    
    def __init__(self):
        self.registry = workflow_registry
        logger.info("Orchestrator initialized")
    
    async def execute_workflow(
        self,
        workflow_name: str,
        context: Dict[str, Any],
        user_id: Optional[int] = None,
        shop_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow
        
        Args:
            workflow_name: Name of workflow to execute
            context: Input context for workflow
            user_id: Optional user ID
            shop_id: Optional shop ID
            
        Returns:
            Workflow execution result
        """
        workflow_id = str(uuid4())
        
        logger.info(
            f"Executing workflow: {workflow_name}, "
            f"workflow_id={workflow_id}, user_id={user_id}, shop_id={shop_id}"
        )
        
        # Check if workflow exists
        if not self.registry.exists(workflow_name):
            error_msg = f"Workflow '{workflow_name}' not found"
            logger.error(error_msg)
            return {
                "workflow_id": workflow_id,
                "status": "error",
                "error": error_msg
            }
        
        # Save workflow state to database when storage is available.
        try:
            await self._save_workflow_state(
                workflow_id=workflow_id,
                workflow_name=workflow_name,
                user_id=user_id,
                shop_id=shop_id,
                status=WorkflowStatus.PENDING,
                input_data=context
            )
        except Exception as state_error:
            logger.warning(
                "Unable to persist initial workflow state for %s: %s",
                workflow_id,
                state_error
            )
        
        try:
            # Create workflow instance
            workflow = self.registry.create(workflow_name)
            
            # Update status to running if workflow state persistence is available.
            try:
                await self._update_workflow_status(workflow_id, WorkflowStatus.RUNNING)
            except Exception as state_error:
                logger.warning(
                    "Unable to set RUNNING status for %s: %s",
                    workflow_id,
                    state_error
                )
            
            # Execute workflow
            logger.info(f"Starting workflow execution: {workflow_id}")
            result = await workflow.run(
                context=context,
                workflow_id=workflow_id,
                user_id=user_id,
                shop_id=shop_id
            )
            
            # Update status to completed if persistence is available.
            try:
                await self._update_workflow_status(
                    workflow_id,
                    WorkflowStatus.COMPLETED,
                    output_data=result
                )
            except Exception as state_error:
                logger.warning(
                    "Unable to set COMPLETED status for %s: %s",
                    workflow_id,
                    state_error
                )
            
            logger.info(f"Workflow completed: {workflow_id}")
            
            return {
                "workflow_id": workflow_id,
                "status": "completed",
                "result": result
            }
        
        except Exception as e:
            logger.error(f"Workflow failed: {workflow_id}, error: {e}")
            
            # Try to persist failure status, but do not mask the original failure.
            try:
                await self._update_workflow_status(
                    workflow_id,
                    WorkflowStatus.FAILED,
                    error=str(e)
                )
            except Exception as state_error:
                logger.warning(
                    "Unable to set FAILED status for %s: %s",
                    workflow_id,
                    state_error
                )
            
            return {
                "workflow_id": workflow_id,
                "status": "failed",
                "error": str(e)
            }
    
    async def execute_workflow_from_event(
        self,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Execute workflow triggered by an event
        
        Args:
            event_type: Type of event
            event_data: Event data including shop_id, user_id, etc.
            
        Returns:
            Workflow result or None if no workflow for this event
        """
        # Map events to workflows
        event_to_workflow = {
            "LOW_STOCK": "inventory_workflow",
            "NEGATIVE_REVIEW": "review_workflow",
            "PRICE_CHANGED": "pricing_workflow",
            "SALES_DROP": "sales_analysis_workflow",
        }
        
        workflow_name = event_to_workflow.get(event_type)
        
        if not workflow_name:
            logger.debug(f"No workflow mapped for event: {event_type}")
            return None
        
        logger.info(f"Event {event_type} triggered workflow: {workflow_name}")
        
        return await self.execute_workflow(
            workflow_name=workflow_name,
            context=event_data,
            user_id=event_data.get("user_id"),
            shop_id=event_data.get("shop_id")
        )
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get workflow execution status
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Workflow status dict or None
        """
        async with db_manager.get_async_session() as db:
            from database.repositories.workflow_state import workflow_state_repository
            
            workflow_state = await workflow_state_repository.get_by_workflow_id(
                db, workflow_id
            )
            
            if not workflow_state:
                return None
            
            return workflow_state.to_dict()
    
    async def _save_workflow_state(
        self,
        workflow_id: str,
        workflow_name: str,
        user_id: Optional[int],
        shop_id: Optional[int],
        status: WorkflowStatus,
        input_data: Dict[str, Any]
    ):
        """Save initial workflow state to database"""
        async with db_manager.get_async_session() as db:
            from database.repositories.workflow_state import workflow_state_repository
            
            await workflow_state_repository.create(db, {
                "workflow_id": workflow_id,
                "user_id": user_id,
                "shop_id": shop_id,
                "workflow_type": "langgraph",
                "workflow_name": workflow_name,
                "status": status,
                "input_data": input_data,
                "started_at": datetime.utcnow()
            })
            
            logger.debug(f"Saved workflow state: {workflow_id}")
    
    async def _update_workflow_status(
        self,
        workflow_id: str,
        status: WorkflowStatus,
        output_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        """Update workflow status in database"""
        async with db_manager.get_async_session() as db:
            from database.repositories.workflow_state import workflow_state_repository
            
            workflow_state = await workflow_state_repository.get_by_workflow_id(
                db, workflow_id
            )
            
            if not workflow_state:
                logger.error(f"Workflow state not found: {workflow_id}")
                return
            
            update_data = {
                "status": status
            }
            
            if status in (WorkflowStatus.COMPLETED, WorkflowStatus.FAILED):
                update_data["completed_at"] = datetime.utcnow()
            
            if output_data:
                update_data["output_data"] = output_data
            
            if error:
                update_data["error"] = error
            
            await workflow_state_repository.update(db, workflow_state.id, update_data)
            logger.debug(f"Updated workflow status: {workflow_id} -> {status}")


# Global orchestrator instance
orchestrator = Orchestrator()
